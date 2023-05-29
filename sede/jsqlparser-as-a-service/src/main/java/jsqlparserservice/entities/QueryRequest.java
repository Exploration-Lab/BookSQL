package jsqlparserservice.entities;

import lombok.*;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
@Getter
public class QueryRequest {
    private String sql;
}
