import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.ObjectMapper;

enum Severity {
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

class TestJackson {
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        Severity s = mapper.readValue("\"CRITICAL\"", Severity.class);
        System.out.println("Result: " + s);
    }
}
