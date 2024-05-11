package jsqlparserservice.utils;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.*;
import org.springframework.stereotype.Component;

@Component
public class JsonMapper {
    private final ObjectMapper objectMapper;

    public JsonMapper(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
        this.objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }

    public JsonNode convert(Object obj) {
        return objectMapper.valueToTree(obj);
    }

    public String convertObjToString(Object obj) throws JsonProcessingException {
        return objectMapper.writeValueAsString(obj);
    }

    public JsonNode convertStringToJsonNode(String jsonStr) throws JsonProcessingException {
        return objectMapper.readTree(jsonStr);
    }
}
