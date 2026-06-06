use crate::{
    config::{Edge, Layout},
    protocol::{InputEvent, PeerMessage},
};

const REMOTE_ENTRY_INSET: f64 = 1.0;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ActiveTarget {
    Local,
    Remote,
}

#[derive(Debug)]
pub struct RouteDecision {
    pub suppress_local: bool,
    pub messages: Vec<PeerMessage>,
}

#[derive(Debug)]
pub struct InputRouter {
    layout: Layout,
    active: ActiveTarget,
    last_local_mouse: Option<(f64, f64)>,
    remote_mouse: (f64, f64),
}

impl InputRouter {
    pub fn new(layout: Layout) -> Self {
        let remote_mouse = match layout.remote_edge {
            Edge::Right => (REMOTE_ENTRY_INSET, layout.remote_height / 2.0),
            Edge::Left => (
                layout.remote_width - 1.0 - REMOTE_ENTRY_INSET,
                layout.remote_height / 2.0,
            ),
            Edge::Top => (
                layout.remote_width / 2.0,
                layout.remote_height - 1.0 - REMOTE_ENTRY_INSET,
            ),
            Edge::Bottom => (layout.remote_width / 2.0, REMOTE_ENTRY_INSET),
        };

        Self {
            layout,
            active: ActiveTarget::Local,
            last_local_mouse: None,
            remote_mouse,
        }
    }

    pub fn handle_captured(&mut self, event: InputEvent) -> RouteDecision {
        match event {
            InputEvent::MouseMove { x, y } => self.handle_mouse_move(x, y),
            other => {
                if self.active == ActiveTarget::Remote {
                    RouteDecision {
                        suppress_local: true,
                        messages: vec![PeerMessage::Input { event: other }],
                    }
                } else {
                    RouteDecision {
                        suppress_local: false,
                        messages: Vec::new(),
                    }
                }
            }
        }
    }

    pub fn set_remote_display(&mut self, width: f64, height: f64) {
        if width <= 0.0 || height <= 0.0 {
            return;
        }

        self.layout.remote_width = width;
        self.layout.remote_height = height;
        self.remote_mouse.0 = self
            .remote_mouse
            .0
            .clamp(0.0, self.layout.remote_width - 1.0);
        self.remote_mouse.1 = self
            .remote_mouse
            .1
            .clamp(0.0, self.layout.remote_height - 1.0);
    }

    pub fn set_local_display(&mut self, width: f64, height: f64) {
        if width <= 0.0 || height <= 0.0 {
            return;
        }

        self.layout.local_width = width;
        self.layout.local_height = height;
        if let Some((x, y)) = self.last_local_mouse {
            self.last_local_mouse = Some((
                x.clamp(0.0, self.layout.local_width - 1.0),
                y.clamp(0.0, self.layout.local_height - 1.0),
            ));
        }
    }

    fn handle_mouse_move(&mut self, x: f64, y: f64) -> RouteDecision {
        let previous = self.last_local_mouse.replace((x, y));

        if self.active == ActiveTarget::Local {
            if self.crosses_to_remote(x, y) {
                self.active = ActiveTarget::Remote;
                self.remote_mouse = self.remote_entry_point(x, y);
                return RouteDecision {
                    suppress_local: true,
                    messages: vec![
                        PeerMessage::Active {
                            remote_active: true,
                        },
                        PeerMessage::Input {
                            event: InputEvent::MouseMove {
                                x: self.remote_mouse.0,
                                y: self.remote_mouse.1,
                            },
                        },
                    ],
                };
            }

            return RouteDecision {
                suppress_local: false,
                messages: Vec::new(),
            };
        }

        let (dx, dy) = previous
            .map(|(last_x, last_y)| (x - last_x, y - last_y))
            .unwrap_or((0.0, 0.0));
        self.remote_mouse.0 = (self.remote_mouse.0 + dx).clamp(0.0, self.layout.remote_width - 1.0);
        self.remote_mouse.1 =
            (self.remote_mouse.1 + dy).clamp(0.0, self.layout.remote_height - 1.0);

        if self.crosses_back_to_local() {
            self.active = ActiveTarget::Local;
            return RouteDecision {
                suppress_local: true,
                messages: vec![PeerMessage::Active {
                    remote_active: false,
                }],
            };
        }

        RouteDecision {
            suppress_local: true,
            messages: vec![PeerMessage::Input {
                event: InputEvent::MouseMove {
                    x: self.remote_mouse.0,
                    y: self.remote_mouse.1,
                },
            }],
        }
    }

    fn crosses_to_remote(&self, x: f64, y: f64) -> bool {
        match self.layout.remote_edge {
            Edge::Right => x >= self.layout.local_width - 1.0,
            Edge::Left => x <= 0.0,
            Edge::Top => y <= 0.0,
            Edge::Bottom => y >= self.layout.local_height - 1.0,
        }
    }

    fn crosses_back_to_local(&self) -> bool {
        match self.layout.remote_edge {
            Edge::Right => self.remote_mouse.0 <= 0.0,
            Edge::Left => self.remote_mouse.0 >= self.layout.remote_width - 1.0,
            Edge::Top => self.remote_mouse.1 >= self.layout.remote_height - 1.0,
            Edge::Bottom => self.remote_mouse.1 <= 0.0,
        }
    }

    fn remote_entry_point(&self, x: f64, y: f64) -> (f64, f64) {
        match self.layout.remote_edge {
            Edge::Right => (
                REMOTE_ENTRY_INSET,
                scale(y, self.layout.local_height, self.layout.remote_height),
            ),
            Edge::Left => (
                self.layout.remote_width - 1.0 - REMOTE_ENTRY_INSET,
                scale(y, self.layout.local_height, self.layout.remote_height),
            ),
            Edge::Top => (
                scale(x, self.layout.local_width, self.layout.remote_width),
                self.layout.remote_height - 1.0 - REMOTE_ENTRY_INSET,
            ),
            Edge::Bottom => (
                scale(x, self.layout.local_width, self.layout.remote_width),
                REMOTE_ENTRY_INSET,
            ),
        }
    }
}

fn scale(value: f64, source_extent: f64, target_extent: f64) -> f64 {
    if source_extent <= 1.0 {
        return 0.0;
    }
    let ratio = (value / (source_extent - 1.0)).clamp(0.0, 1.0);
    ratio * (target_extent - 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn layout(edge: Edge) -> Layout {
        Layout {
            local_width: 100.0,
            local_height: 50.0,
            remote_width: 80.0,
            remote_height: 40.0,
            remote_edge: edge,
        }
    }

    #[test]
    fn activates_remote_on_configured_edge() {
        let mut router = InputRouter::new(layout(Edge::Right));

        let decision = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 25.0 });

        assert!(decision.suppress_local);
        assert!(matches!(
            decision.messages.first(),
            Some(PeerMessage::Active {
                remote_active: true
            })
        ));
    }

    #[test]
    fn forwards_keyboard_while_remote_is_active() {
        let mut router = InputRouter::new(layout(Edge::Right));
        let _ = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 25.0 });

        let decision = router.handle_captured(InputEvent::KeyPress {
            key: "KeyA".to_string(),
            text: Some("a".to_string()),
        });

        assert!(decision.suppress_local);
        assert!(matches!(
            decision.messages.as_slice(),
            [PeerMessage::Input {
                event: InputEvent::KeyPress { .. }
            }]
        ));
    }

    #[test]
    fn entering_remote_does_not_immediately_cross_back_on_zero_delta() {
        let mut router = InputRouter::new(layout(Edge::Right));
        let _ = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 25.0 });

        let decision = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 25.0 });

        assert!(decision.suppress_local);
        assert!(matches!(
            decision.messages.as_slice(),
            [PeerMessage::Input {
                event: InputEvent::MouseMove { .. }
            }]
        ));
    }

    #[test]
    fn crosses_back_to_local_from_remote_edge() {
        let mut router = InputRouter::new(layout(Edge::Right));
        let _ = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 25.0 });

        let decision = router.handle_captured(InputEvent::MouseMove { x: 98.0, y: 25.0 });

        assert!(decision.suppress_local);
        assert!(matches!(
            decision.messages.as_slice(),
            [PeerMessage::Active {
                remote_active: false
            }]
        ));
    }

    #[test]
    fn updates_remote_display_before_edge_entry() {
        let mut router = InputRouter::new(layout(Edge::Right));
        router.set_remote_display(200.0, 100.0);

        let decision = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 49.0 });

        assert!(matches!(
            decision.messages.as_slice(),
            [
                PeerMessage::Active {
                    remote_active: true
                },
                PeerMessage::Input {
                    event: InputEvent::MouseMove { x: 1.0, y }
                }
            ] if (*y - 99.0).abs() < f64::EPSILON
        ));
    }

    #[test]
    fn updates_local_display_before_edge_detection() {
        let mut router = InputRouter::new(layout(Edge::Right));
        router.set_local_display(200.0, 100.0);

        let local_decision = router.handle_captured(InputEvent::MouseMove { x: 99.0, y: 50.0 });
        assert!(!local_decision.suppress_local);
        assert!(local_decision.messages.is_empty());

        let remote_decision = router.handle_captured(InputEvent::MouseMove { x: 199.0, y: 99.0 });
        assert!(matches!(
            remote_decision.messages.as_slice(),
            [
                PeerMessage::Active {
                    remote_active: true
                },
                PeerMessage::Input {
                    event: InputEvent::MouseMove { x: 1.0, y }
                }
            ] if (*y - 39.0).abs() < f64::EPSILON
        ));
    }
}
