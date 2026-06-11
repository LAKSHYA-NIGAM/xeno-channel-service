CHANNEL_PROBABILITIES = {
    "whatsapp": {
        "delivered": 0.95,
        "read":      0.85,
        "clicked":   0.75,
    },
    "email": {
        "delivered": 0.90,
        "opened":    0.75,
        "clicked":   0.60,
    },
    "sms": {
        "delivered": 0.95,
        "clicked":   0.50,
    },
}

# Delay ranges in seconds between each event stage (min, max)
# Simulates real-world async delivery timing but optimized for fast automated verification
EVENT_DELAYS = {
    "sent":      (0.5, 1.5),
    "delivered": (1.0, 2.5),
    "opened":    (1.0, 3.0),
    "read":      (1.0, 3.0),
    "clicked":   (1.5, 4.0),
}

