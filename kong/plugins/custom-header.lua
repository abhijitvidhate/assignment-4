-- Custom Kong plugin: injects a custom response header

local kong = kong

local CustomHeader = {
  PRIORITY = 1000,
  VERSION = "1.0",
}

function CustomHeader:header_filter(conf)
  kong.response.set_header("X-Assignment", "Talentica-Kong")
end

return CustomHeader
