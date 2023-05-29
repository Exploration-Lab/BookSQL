package jsqlparserservice.exceptions;

public class UnableToParseQueryException extends RuntimeException {
    public UnableToParseQueryException(String message, Exception e) {
        super(message);
    }
}
