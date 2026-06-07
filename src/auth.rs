use anyhow::{Context, Result, bail};
use hmac::{Hmac, Mac};
use rand::random;
use sha2::Sha256;

use crate::{
    config::{AuthConfig, Role},
    protocol::{DisplayGeometry, HelloAuth},
};

type HmacSha256 = Hmac<Sha256>;

const DOMAIN: &str = "anyuniversalcontrol-hello-auth-v1";

pub fn hello_auth(
    auth: &AuthConfig,
    node_name: &str,
    role: Role,
    local_display: DisplayGeometry,
) -> Result<Option<HelloAuth>> {
    let Some(secret) = auth.normalized_shared_secret() else {
        return Ok(None);
    };

    let nonce = random_nonce();
    let proof = proof_hex(secret.as_bytes(), node_name, role, local_display, &nonce)?;
    Ok(Some(HelloAuth { nonce, proof }))
}

pub fn verify_hello_auth(
    auth: &AuthConfig,
    node_name: &str,
    role: Role,
    local_display: DisplayGeometry,
    hello_auth: Option<&HelloAuth>,
) -> Result<()> {
    let Some(secret) = auth.normalized_shared_secret() else {
        return Ok(());
    };
    let Some(hello_auth) = hello_auth else {
        bail!("peer hello did not include required auth proof");
    };

    let proof = decode_hex(&hello_auth.proof).context("peer hello auth proof is not valid hex")?;
    let mac = hello_mac(
        secret.as_bytes(),
        node_name,
        role,
        local_display,
        &hello_auth.nonce,
    )?;
    mac.verify_slice(&proof)
        .map_err(|_| anyhow::anyhow!("peer hello auth proof did not match shared secret"))
}

fn random_nonce() -> String {
    encode_hex(&random::<[u8; 16]>())
}

fn proof_hex(
    secret: &[u8],
    node_name: &str,
    role: Role,
    local_display: DisplayGeometry,
    nonce: &str,
) -> Result<String> {
    let mac = hello_mac(secret, node_name, role, local_display, nonce)?;
    let bytes = mac.finalize().into_bytes();
    Ok(encode_hex(&bytes))
}

fn hello_mac(
    secret: &[u8],
    node_name: &str,
    role: Role,
    local_display: DisplayGeometry,
    nonce: &str,
) -> Result<HmacSha256> {
    let mut mac =
        HmacSha256::new_from_slice(secret).context("failed to initialize hello auth HMAC")?;
    mac.update(DOMAIN.as_bytes());
    mac.update(b"\n");
    mac.update(node_name.as_bytes());
    mac.update(b"\n");
    mac.update(format!("{role:?}").as_bytes());
    mac.update(b"\n");
    mac.update(format!("{:.3}x{:.3}", local_display.width, local_display.height).as_bytes());
    mac.update(b"\n");
    mac.update(nonce.as_bytes());
    Ok(mac)
}

fn encode_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}

fn decode_hex(value: &str) -> Result<Vec<u8>> {
    if !value.len().is_multiple_of(2) {
        bail!("hex value must contain an even number of digits");
    }

    let mut out = Vec::with_capacity(value.len() / 2);
    let bytes = value.as_bytes();
    for pair in bytes.chunks_exact(2) {
        let high = hex_digit(pair[0])?;
        let low = hex_digit(pair[1])?;
        out.push((high << 4) | low);
    }
    Ok(out)
}

fn hex_digit(value: u8) -> Result<u8> {
    match value {
        b'0'..=b'9' => Ok(value - b'0'),
        b'a'..=b'f' => Ok(value - b'a' + 10),
        b'A'..=b'F' => Ok(value - b'A' + 10),
        _ => bail!("invalid hex digit"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::AuthConfig;

    fn display() -> DisplayGeometry {
        DisplayGeometry {
            width: 1920.0,
            height: 1080.0,
        }
    }

    #[test]
    fn hello_auth_round_trips_with_shared_secret() {
        let auth = AuthConfig {
            shared_secret: Some("test-secret".to_string()),
        };
        let hello = hello_auth(&auth, "owner", Role::InputOwner, display())
            .unwrap()
            .unwrap();

        verify_hello_auth(&auth, "owner", Role::InputOwner, display(), Some(&hello)).unwrap();
    }

    #[test]
    fn hello_auth_rejects_wrong_secret() {
        let sender = AuthConfig {
            shared_secret: Some("sender-secret".to_string()),
        };
        let receiver = AuthConfig {
            shared_secret: Some("receiver-secret".to_string()),
        };
        let hello = hello_auth(&sender, "owner", Role::InputOwner, display())
            .unwrap()
            .unwrap();

        let error = verify_hello_auth(
            &receiver,
            "owner",
            Role::InputOwner,
            display(),
            Some(&hello),
        )
        .unwrap_err();

        assert!(error.to_string().contains("auth proof did not match"));
    }

    #[test]
    fn hello_auth_is_optional_when_secret_is_absent() {
        let auth = AuthConfig::default();

        assert!(
            hello_auth(&auth, "owner", Role::InputOwner, display())
                .unwrap()
                .is_none()
        );
        verify_hello_auth(&auth, "owner", Role::InputOwner, display(), None).unwrap();
    }
}
