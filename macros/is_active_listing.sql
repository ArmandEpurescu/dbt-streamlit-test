{% macro is_active_listing(metric_date_col, created_at_col, updated_at_col) -%}
(
    {{ created_at_col }} <= {{ metric_date_col }}
    and {{ updated_at_col }} >= {{ metric_date_col }} - interval 30 day
)
{%- endmacro %}
