package com.ummalqura;

/**
 * Structured error response
 */
public class CalendarError extends RuntimeException {
    private final ErrorCode errorCode;
    private final String field;
    private final Object value;

    public CalendarError(ErrorCode errorCode, String message) {
        this(errorCode, message, null, null);
    }

    public CalendarError(ErrorCode errorCode, String message, String field, Object value) {
        super(message);
        this.errorCode = errorCode;
        this.field = field;
        this.value = value;
    }

    public ErrorCode getErrorCode() {
        return errorCode;
    }

    public String getField() {
        return field;
    }

    public Object getValue() {
        return value;
    }

    public String toJson() {
        StringBuilder sb = new StringBuilder();
        sb.append("{\"error_code\":\"").append(errorCode.getValue()).append("\"");
        sb.append(",\"message\":\"").append(getMessage()).append("\"");
        if (field != null) {
            sb.append(",\"field\":\"").append(field).append("\"");
        }
        if (value != null) {
            sb.append(",\"value\":").append(value);
        }
        sb.append("}");
        return sb.toString();
    }
}
