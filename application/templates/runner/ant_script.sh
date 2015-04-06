
ant -buildfile {{buildfile_name}} compile_src && echo "THE SOURCE WAS COMPILED SUCCESFULLY"
{% if has_tests %}
{% if has_class_files %}
ant -buildfile {{buildfile_name}} move_tests 
{% else %}
ant -buildfile {{buildfile_name}} compile_tests 
{% endif %}
ant -buildfile {{buildfile_name}} delete_test_source
timeout -s 9 {{test_timeout}} ant -buildfile {{buildfile_name}} test
{% endif %}