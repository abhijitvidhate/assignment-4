local kong = kong
function add_custom_header()
  kong.response.set_header("X-Custom-Header", "Talentica-Assignment")
end
return { header_filter = add_custom_header }
