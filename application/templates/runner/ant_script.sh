
ant -buildfile {{buildfile_name}} compile
{% if has_tests %}
ant -buildfile {{buildfile_name}} cleantestsrc
timeout -s 9 {{test_timeout}} ant -buildfile {{buildfile_name}} test
{% endif %}
