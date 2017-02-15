var simpleAjaxTable = {}

simpleAjaxTable.flushPagination = function(limit, page, count) {
  var page_max = Math.ceil(count / limit)

  var html = ""

  if(page_max <= 4) {
    html += '<li class="page-item page-prev"><a class="page-link" href="javascript:void(0)"><i class="fa fa-angle-left"></i></a></li>'
    for(var i = 1; i < page; ++i) {
      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + i + '</a></li>'
    }
    html += '<li class="page-item active"><a class="page-link" href="javascript:void(0)">' + page + '</a></li>'
    for(var i = page + 1; i <= page_max; ++i) {
      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + i + '</a></li>'
    }
    html += '<li class="page-item page-next"><a class="page-link" href="javascript:void(0)"><i class="fa fa-angle-right"></i></a></li>'
  } else {
    html += '<li class="page-item page-prev"><a class="page-link" href="javascript:void(0)"><i class="fa fa-angle-left"></i></a></li>'
    if(page == 1) {
      html += '<li class="page-item active"><a class="page-link" href="javascript:void(0)">' + page + '</a></li>'
      for(var i = page + 1; i <= 3; ++i) {
        html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + i + '</a></li>'
      }
      html += '<li class="page-item disabled"><a class="page-link" href="javascript:void(0)">' + '…' + '</a></li>'
      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + page_max + '</a></li>'
    } else if (page >= page_max-2) {

      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + 1 + '</a></li>'
      html += '<li class="page-item disabled"><a class="page-link" href="javascript:void(0)">' + '…' + '</a></li>'
      for(var i = page_max - 2; i < page; ++i) {
        html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + i + '</a></li>'
      }
      html += '<li class="page-item active"><a class="page-link" href="javascript:void(0)">' + page + '</a></li>'
      for(var i = page + 1; i <= page_max; ++i) {
        html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + i + '</a></li>'
      }
    } else {
      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + (page-1) + '</a></li>'
      html += '<li class="page-item active"><a class="page-link" href="javascript:void(0)">' + page + '</a></li>'
      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + (page+1) + '</a></li>'
      html += '<li class="page-item disabled"><a class="page-link" href="javascript:void(0)">' + '…' + '</a></li>'
      html += '<li class="page-item"><a class="page-link" href="javascript:void(0)">' + page_max + '</a></li>'
    }
    html += '<li class="page-item page-next"><a class="page-link" href="javascript:void(0)"><i class="fa fa-angle-right"></i></a></li>'
  }

  var pg = $("."+this.tablePaginationClass)
  $(pg).find("a").unbind("click")
  $(pg).empty().append(html)

  if(page == 1) {
    $(".page-prev").addClass("disabled")
  }
  if(page == page_max) {
    $(".page-next").addClass("disabled")
  }

  $("."+this.tablePaginationClass+" li a").click(function() {
    text = $(this).text()
    if(text == "") {
      if($(this).find("i").hasClass("fa-angle-left")) {
        simpleAjaxTable.page -= 1
      } else {
        simpleAjaxTable.page += 1
      }
    } else {
      simpleAjaxTable.page = parseInt(text)
    }

    simpleAjaxTable.flushTable()
  })
}


simpleAjaxTable.flushTable = function() {
  var limit = parseInt($("#"+this.tablePageNumber).find("option:selected").text())
  var page = this.page
  var search = this.search != null ? this.search : ""
  var filterData = this.filterData != null ? this.filterData : {}
  var base_url = this.base_url

  var ordering = []
  for(var i in this.column) {
    if(this.column[i].sort) {
      var info = ""
      if(this.column[i].ordering < 0) {
        info += "-"
      } else if(this.column[i].ordering == 0) {
        continue
      }
      info += this.column[i].name
      ordering.push(info)
    }
  }
  var request = this.requestGenerator(limit, page, filterData, search, ordering)

  var SAT = this

  $.ajax({
    type: request.type,
    url: request.url,
    dataType: request.dataType,
    data: request.data,
    success: function(ret) {
      var column = simpleAjaxTable.column
      var html = ""
      for(var i in column) {
        var c = column[i]
        var caption = c.caption
        if(c.sort) {
          if(c.ordering == 1) {
            html += '<th nowrap>'+caption+' <a cname="'+c.name+'" class="'+simpleAjaxTable.orderingBtn+'" href="javascript:void(0)"><i class="fa fa-angle-up"></i></a></th>'
          } else if(c.ordering == -1) {
            html += '<th nowrap>'+caption+' <a cname="'+c.name+'" class="'+simpleAjaxTable.orderingBtn+'" href="javascript:void(0)"><i class="fa fa-angle-down"></i></a></th>'
          } else {
            html += '<th nowrap>'+caption+' <a cname="'+c.name+'" class="'+simpleAjaxTable.orderingBtn+'" href="javascript:void(0)"><i class="fa fa-circle-thin"></i></a></th>'
          }
        } else {
          html += '<th nowrap>'+caption+'</th>'
        }
      }
      $('#'+simpleAjaxTable.tableHeadTr).empty().append(html)

      $("."+simpleAjaxTable.orderingBtn).click(function() {
        var cname = $(this).attr("cname")
        for(var i in column) {
          if(column[i].name == cname) {
            var o = column[i].ordering
            o += 1
            if(o > 1) {
              o = -1
            }
            column[i].ordering = o
            simpleAjaxTable.flushTable()
            return
          }
        }
      })

      var tbody = $("#"+simpleAjaxTable.tableBody)
      var generatedData = simpleAjaxTable.dataGenerator(ret)

      $(tbody).empty()
      for(var i in generatedData.results) {
        html = '<tr>'

        var line = generatedData.results[i]

        for(var i in column) {
          var name = column[i].name
          var info = line[name]

          if(column[i].type == "datetime") {
            var iDate = new Date(info)
            info = iDate.toLocaleString()
          }
          if(column[i].type == "link") {
            var key = column[i].key
            key = line[key]
            var url = base_url + key
            info = '<a href="'+url+'">'+info+'</a>'
          }

          html += '<td>'+info+'</td>'
        }

        html += '</tr>'
        $(tbody).append(html)
      }

      SAT.flushPagination(limit, page, ret.count)
    }
  })
}

simpleAjaxTable.init = function(table_info) {
  this.id = table_info.id
  this.title = table_info.title
  this.column = table_info.column
  this.filter = table_info.filter
  this.requestGenerator = table_info.requestGenerator
  this.dataGenerator = table_info.dataGenerator
  this.page = table_info.page == null ? 1 : table_info.page
  this.base_url = table_info.base_url

  this.tableID = this.id + 'SAT'
  this.tableFilterBtn = this.tableID + "FBTN"
  this.tableFilter = this.tableID + "F"
  this.tableFilterDiv = this.tableFilter + "D"
  this.tableSearchForm = this.tableID + "SF"
  this.tableSearchInput = this.tableID + "SI"
  this.tablePageNumberForm = this.tableID + "PNF"
  this.tablePageNumber = this.tableID + "PN"
  this.tablePaginationClass = this.tableID + "PC"
  this.tableHeadTr = this.tableID + "THTR"
  this.tableBody = this.tableID + "TB"
  this.orderingBtn = this.tableID + "OBTN"

  var createBtn = this.tableID + "CBTN"

$('#' + this.id).append(
'<div class="container">\
  <div class="row justify-content-between">\
    <div>\
      <h2>'+this.title+'</h2>\
    </div>\
    <div>\
      <button id="'+this.tableFilterBtn+'" type="button" class="btn btn-outline-primary" data-toggle="collapse" data-target="#'+this.tableFilterDiv+'">筛选</button>\
      <a type="button" class="btn btn-primary" id="'+createBtn+'">创建</a>\
    </div>\
  </div>\
  <div class="container jumbotron bg-faded collapse" id="'+this.tableFilterDiv+'">\
    <form class="form" id="'+this.tableFilter+'" onsubmit="return false;">\
    </form>\
  </div>\
  <div class="row justify-content-between">\
    <div class="col-md-5 col-sm-12">\
      <form class="form" id="'+this.tableSearchForm+'" onsubmit="return false;">\
        <div class="form-group row">\
          <label for="'+this.tableSearchInput+'" class="sr-only">搜索</label>\
          <div class="col-xs-12 input-group">\
            <input type="text" class="form-control" name="search" id="'+this.tableSearchInput+'" placeholder="搜索">\
            <span class="input-group-btn">\
              <button type="submit" class="btn btn-primary"><i class="fa fa-search"></i></button>\
            </span>\
          </div>\
        </div>\
      </form>\
    </div>\
    <div class="col-md-6 col-sm-12">\
      <nav aria-label="Page navigation" style="float:right;">\
        <ul class="pagination '+this.tablePaginationClass+'">\
        </ul>\
      </nav>\
    </div>\
  </div>\
  <div>\
    <table class="table table-hover">\
      <thead>\
        <tr id="'+this.tableHeadTr+'">\
        </tr>\
      </thead>\
      <tbody id="'+this.tableBody+'">\
      </tbody>\
    </table>\
  </div>\
  <div class="row justify-content-between">\
    <div class="col-md-5">\
      <form id="'+this.tablePageNumberForm+'">\
        <div class="form-group row">\
          <label class="col-md-4 col-form-label" for="'+this.tablePageNumber+'">每页</label>\
          <div class="col-md-8">\
            <select class="form-control" id="'+this.tablePageNumber+'">\
              <option>5</option>\
              <option>10</option>\
              <option selected="selected">20</option>\
              <option>50</option>\
              <option>100</option>\
              <option>200</option>\
            </select>\
          </div>\
        </div>\
      </form>\
    </div>\
    <div class="col-md-6">\
      <nav aria-label="Page navigation" style="float:right;">\
        <ul class="pagination '+this.tablePaginationClass+'">\
       </ul>\
      </nav>\
    </div>\
  </div>\
</div>'
)

  if(table_info.create_url == null) {
    $("#"+createBtn).remove()
  } else {
    $("#"+createBtn).attr("href", table_info.create_url)
  }

  if(this.filter == null || this.filter.length == 0) {
    $("#"+this.tableFilterDiv).remove()
    $("#"+this.tableFilterBtn).remove()
  } else {
    var filterForm = $("#"+this.tableFilter)
    var filter = this.filter
    for(var i in filter) {
      var info = filter[i]

      $(filterForm).append(
'      <div class="form-group row">\
        <label for="'+(simpleAjaxTable.tableID+info.name)+'" class="col-md-3 col-form-label">'+info.caption+'</label>\
        <div class="col-md-9">\
          <input type="'+info.type+'" class="form-control" name="'+info.name+'" id="'+(simpleAjaxTable.tableID+info.name)+'" placeholder="'+info.placeholder+'">\
        </div>\
      </div>'
      )
    }
    $(filterForm).append(
'      <span class="input-group-btn">\
        <button type="submit" class="btn btn-info col-xs-12">查询</button>\
      </span>'
    )

    $(filterForm).submit(function() {
      simpleAjaxTable.filterData = getFormData(filterForm)
      simpleAjaxTable.flushTable()
    })
  }

  this.flushTable()

  $("#"+this.tablePageNumber).change(function() {
    simpleAjaxTable.flushTable()
  })

  $("#"+this.tableSearchForm).submit(function() {
    simpleAjaxTable.search = $("#"+simpleAjaxTable.tableSearchInput).val()
    simpleAjaxTable.flushTable()
  })
}