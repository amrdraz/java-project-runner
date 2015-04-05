
ant -buildfile {{buildfile_name}} compile_src && echo "THE SOURCE WAS COMPILED SUCCESFULLY"
{% if has_tests %}
ant -buildfile {{buildfile_name}} compile_tests 
ant -buildfile {{buildfile_name}} delete_test_source
timeout -s 9 {{test_timeout}} ant -buildfile {{buildfile_name}} test
{% endif %}