package com.codereviewai.models;

import com.fasterxml.jackson.annotation.JsonCreator;

public enum Severity {
    HIGH, MEDIUM, LOW;

    @JsonCreator
    public static Severity fromString(String value) {
        if (value == null) return MEDIUM;
        return switch (value.toUpperCase()) {
            case "CRITICAL", "HIGH", "SEVERE", "FATAL", "ERROR" -> HIGH;
            case "LOW", "MINOR", "INFO", "NOTICE" -> LOW;
            default -> MEDIUM;
        };
    }
}
