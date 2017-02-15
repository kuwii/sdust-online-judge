var simpleAjaxTable = {}

simpleAjaxTable.paginationIconClass = {
  "left": "fa fa-angle-left",
  "right": "fa fa-angle-right"
}
simpleAjaxTable.paginationLiClass = {
  "left": "page-item page-prev",
  "right": "page-item page-next",
  "number": "page-item",
  "...": "page-item disabled"
}

simpleAjaxTable.createPaginationButtonLi = function(option) {
  var type = option.type
  var icon = ("<i></i>")
  $(icon).addClass(simpleAjaxTable.paginationIconClass[type])
  var a = $("<a></a>")
  $(a).addClass("page-link").attr("href", "javascript:void(0)").append(icon)
  if (type == "number") {
    var number = option.number
    $(a).text(number)
  } else if (type == "...") {
    $(a).text("…")
  }
  var li = $("<li></li>")
  $(li).addClass(simpleAjaxTable.paginationLiClass[type]).append(a)
  if (option.active == true) {
    $(li).addClass("active")
  }
  return li
}

simpleAjaxTable.flushPagination = function(limit, page, count) {
  var self = this

  var page_max = Math.ceil(count / limit)
  var pg = $("." + self.tablePaginationClass)
  $(pg).find("a").unbind("click")

  $(pg).empty()
  $(pg).append(self.createPaginationButtonLi({type: "left"}))
  if (page_max < 4) {
    for(var i = 1; i < page; ++i) {
      $(pg).append(self.createPaginationButtonLi({type: "number", number: i}))
    }
    $(pg).append(self.createPaginationButtonLi({type: "number", number: page, active: true}))
    for(var i = page + 1; i <= page_max; ++i) {
      $(pg).append(self.createPaginationButtonLi({type: "number", number: i}))
    }
  } else {
    if (page == 1) {
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page, active: true}))
      for(var i = page + 1; i <= 3; ++i) {
        $(pg).append(self.createPaginationButtonLi({type: "number", number: i}))
      }
      $(pg).append(self.createPaginationButtonLi({type: "..."}))
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page_max}))
    } else if (page >= page_max-2) {
      $(pg).append(self.createPaginationButtonLi({type: "number", number: 1}))
      $(pg).append(self.createPaginationButtonLi({type: "..."}))
      for(var i = page_max - 2; i < page; ++i) {
        $(pg).append(self.createPaginationButtonLi({type: "number", number: i}))
      }
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page, active: true}))
      for(var i = page + 1; i <= page_max; ++i) {
        $(pg).append(self.createPaginationButtonLi({type: "number", number: i}))
      }
    } else {
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page-1}))
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page, active: true}))
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page+1}))
      $(pg).append(self.createPaginationButtonLi({type: "..."}))
      $(pg).append(self.createPaginationButtonLi({type: "number", number: page_max}))
    }
  }
  $(pg).append(self.createPaginationButtonLi({type: "right"}))

  if(page == 1) {
    $(".page-prev").addClass("disabled")
  }
  if(page == page_max) {
    $(".page-next").addClass("disabled")
  }

  $("."+self.tablePaginationClass+" li a").click(function() {
    text = $(self).text()
    if(text == "") {
      if($(self).find("i").hasClass("fa-angle-left")) {
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
  var self = this

  var limit = parseInt($("#"+self.tablePageNumber).find("option:selected").text())
  var page = self.page
  var search = self.search != null ? self.search : ""
  var filterData = self.filterData != null ? self.filterData : {}
  var ordering = []

  for (var i in self.column) {
    if(self.column[i].sort) {
      var info = ""
      if(self.column[i].ordering < 0) {
        info += "-"
      } else if(self.column[i].ordering == 0) {
        continue
      }
      info += self.column[i].name
      ordering.push(info)
    }
  }

  var request = self.requestGenerator(limit, page, filterData, search, ordering)

  $.ajax({
    type: request.type,
    url: request.url,
    dataType: request.dataType,
    data: request.data,
    success: function(ret) {
      var column = self.column
      var html = ""
      for(var i in column) {
        var c = column[i]
        var caption = c.caption
        if(c.sort) {
          if(c.ordering == 1) {
            html += '<th nowrap>'+caption+' <a cname="'+c.name+'" class="'+self.orderingBtn+'" href="javascript:void(0)"><i class="fa fa-angle-up"></i></a></th>'
          } else if(c.ordering == -1) {
            html += '<th nowrap>'+caption+' <a cname="'+c.name+'" class="'+self.orderingBtn+'" href="javascript:void(0)"><i class="fa fa-angle-down"></i></a></th>'
          } else {
            html += '<th nowrap>'+caption+' <a cname="'+c.name+'" class="'+self.orderingBtn+'" href="javascript:void(0)"><i class="fa fa-circle-thin"></i></a></th>'
          }
        } else {
          html += '<th nowrap>'+caption+'</th>'
        }
      }
      $('#'+self.tableHeadTr).empty().append(html)

      $("."+self.orderingBtn).click(function() {
        var cname = $(this).attr("cname")
        for(var i in column) {
          if(column[i].name == cname) {
            var o = column[i].ordering
            o += 1
            if(o > 1) {
              o = -1
            }
            column[i].ordering = o
            self.flushTable()
            return
          }
        }
      })

      var tbody = $("#"+self.tableBody)
      var generatedData = self.dataGenerator(ret)

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

          html += '<td>'+info+'</td>'
        }

        html += '</tr>'
        $(tbody).append(html)
      }

      self.flushPagination(limit, page, ret.count)
    }
  })

}

simpleAjaxTable.start = function(table_info) {
  var self = this

  this.id = table_info.id
  this.title = table_info.title
  this.column = table_info.column
  this.filter = table_info.filter
  this.requestGenerator = table_info.requestGenerator
  this.dataGenerator = table_info.dataGenerator
  this.page = table_info.page == null ? 1 : table_info.page

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
    <div class="col-md-3">\
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
        <label for="'+(self.tableID+info.name)+'" class="col-md-3 col-form-label">'+info.caption+'</label>\
        <div class="col-md-9">\
          <input type="'+info.type+'" class="form-control" name="'+info.name+'" id="'+(self.tableID+info.name)+'" placeholder="'+info.placeholder+'">\
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
      self.filterData = getFormData(filterForm)
      self.flushTable()
    })
  }

  this.flushTable()

  $("#"+this.tablePageNumber).change(function() {
    self.flushTable()
  })

  $("#"+this.tableSearchForm).submit(function() {
    self.search = $("#"+self.tableSearchInput).val()
    self.flushTable()
  })
}

simpleAjaxTable.newTable = function() {
  var table = {
    paginationLiClass: simpleAjaxTable.paginationLiClass,
    paginationIconClass: simpleAjaxTable.paginationIconClass,
    createPaginationButtonLi: simpleAjaxTable.createPaginationButtonLi,
    flushPagination: simpleAjaxTable.flushPagination,
    flushTable: simpleAjaxTable.flushTable,
    start: simpleAjaxTable.start
  }
  return table
}

simpleAjaxTable.init = function(table_info) {
  var table = simpleAjaxTable.newTable()
  table.start(table_info)
}