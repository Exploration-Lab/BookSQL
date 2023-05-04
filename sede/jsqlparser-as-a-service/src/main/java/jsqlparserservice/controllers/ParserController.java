package jsqlparserservice.controllers;

import com.fasterxml.jackson.databind.JsonNode;
import jsqlparserservice.entities.QueryRequest;
import jsqlparserservice.exceptions.UnableToParseQueryException;
import jsqlparserservice.utils.JsonMapper;
import lombok.extern.slf4j.Slf4j;
import net.sf.jsqlparser.JSQLParserException;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.Select;
import net.sf.jsqlparser.statement.select.SelectBody;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Slf4j
@RestController
public class ParserController {

    private JsonMapper jsonMapper;

    public ParserController(JsonMapper jsonMapper) {
        this.jsonMapper = jsonMapper;
    }

    @PostMapping("/sqltojson")
    public JsonNode sqlToJson(@RequestBody QueryRequest queryRequest) {

        JsonNode parsed_output;

        Statement stmt = null;
        try {
            stmt = CCJSqlParserUtil.parse(queryRequest.getSql());
        } catch (JSQLParserException jsqlParserException) {
            log.warn("Failed To Parse Query Because Query Isn't Supported By JSQL, SQL QUERY: " + queryRequest.getSql(), jsqlParserException);
            throw new UnableToParseQueryException("Unsupported query: " + queryRequest.getSql(), jsqlParserException);
        }
        parsed_output = jsonMapper.convert(stmt);
        return parsed_output;
    }


    @ExceptionHandler(UnableToParseQueryException.class)
    public void unableToParseQueryException(Exception e, HttpServletResponse response) throws IOException {
        response.sendError(HttpServletResponse.SC_BAD_REQUEST, "something went wrong");
    }

}
