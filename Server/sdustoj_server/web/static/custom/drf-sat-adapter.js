var drf_sat_adapter = {}

drf_sat_adapter.requestGenerator = function(limit, page, filter, search, ordering) {
  var requestData = {
    search: search,
    limit: limit,
    offset: (page - 1) * limit
  }
  for(var i in filter) {
    requestData[i] = filter[i]
  }
  var o = ""
  var first = true
  for(var i in ordering) {
    if(first) {
      first = false
    } else {
      o += ','
    }
    o += ordering[i]
  }
  requestData.ordering = o

  return {
    type: "get",
    url: drf_sat_adapter.url,
    dataType: "json",
    data: requestData
  }
}
drf_sat_adapter.dataGenerator = function(ret) {
  return {
    count: ret.count,
    results: ret.results
  }
}

drf_sat_adapter.init_sat_table = function(table_info) {
  this.url = table_info.url
  table_info.requestGenerator = table_info.requestGenerator == null ? this.requestGenerator : table_info.requestGenerator
  table_info.dataGenerator = table_info.dataGenerator == null ? this.dataGenerator : table_info.dataGenerator
  simpleAjaxTable.init(table_info)
}
