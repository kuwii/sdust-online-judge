var SAInfo = {}

SAInfo.Boolean = function(self, item) {
  var options = []
  if (item.defaultTrue) {
    options = [
      { text: '是', value: true, selected: true },
      { text: '否', value: true },
    ]
  } else {
    options = [
      { text: '是', value: true, selected: true },
      { text: '否', value: true },
    ]
  }
  return SATable.getDom.InputSelect(item.name, item.caption, options)
}
SAInfo.Text = function(self, item) {
  var getDom = SATable.getDom
  var typeInfo = item.typeInfo

  var div = getDom.Div('form-group row')
  var label = $('<label class="col-md-3 col-form-label">' + item.caption + '</label>')
  var divInput = SATable.getDom.Div('col-md-9')
  var input
  if (typeInfo && typeInfo.max_length) {
    input = getDom.Input(item.name, '')
    $(input).attr('maxlength', typeInfo.max_length)
  } else {
    input = $('<textarea></textarea>')
    $(input).addClass('form-control').attr('name', item.name)
  }

  $(div).append(label).append(divInput)
  $(divInput).append(input)

  return div
}
SAInfo.Select = function(self, item) {
  var typeInfo = item.typeInfo
  var options = typeInfo.options ? typeInfo.options : []
  var input = SATable.getDom.InputSelect(item.name, item.caption, options)
  var select = $(input).find('select')
  if (typeInfo.many) {
    $(select).attr('multiple', 'multiple')
  }
  if (typeInfo.ajax) {
    SAForm.requestSelectData(self, select, item)
  }

  return input
}
SAInfo.requestSelectData = function(self, selectDom, item) {
  var typeInfo = item.typeInfo
  var ajaxInfo = typeInfo.ajaxInfo
  ajaxInfo.success = function(ret) {
    var data = typeInfo.dataGenerator(ret)
    for (var i in data) {
      var it = data[i]
      var option = $('<option></option>')
      $(option).attr('value', it.value).text(it.text)
      $(selectDom).append(option)
    }
    var responseHandler = typeInfo.responseHandler
    if (responseHandler) {
      responseHandler(self, selectDom, item, ret)
    }
  }
  $.ajax(ajaxInfo)
}

SAInfo.initData = function(self, formInfo) {
  self.info = {}
  self.info.id = formInfo.id
  self.info.getMethod = formInfo.getMethod ? formInfo.getMethod : 'get'
  self.info.updateMethod = formInfo.updateMethod ? formInfo.updateMethod : 'post'
  self.info.getUrl = formInfo.getUrl ? formInfo.getUrl : '/'
  self.info.updateUrl = formInfo.getUrl ? formInfo.updateUrl : null
  self.info.items = formInfo.items ? formInfo.items : []

  self.dom = {}
}

SAInfo.initInfo = function(self) {
  var getDom = SATable.getDom
  var divInfo = getDom.Container('')
  var divLoading = getDom.Container('jumbotron row justify-content-sm-center')

  var divLoadingIcon = getDom.Div('col-xs-1')
  var iconLoading = getDom.IconLoading()
  $(divLoading).append(divLoadingIcon)
  $(divLoadingIcon).append(iconLoading)

  self.dom.divInfo = divInfo
  self.dom.divLoading = divLoading

  $(divInfo).hide()
  $('#'+self.info.id).empty().append(divInfo).append(divLoading)
}

SAInfo.

SATable.SimpleAjaxInfo = function(formInfo) {
  var saInfo = {
    initData: SAInfo.initData,
    initInfo: SAInfo.initInfo
  }
  saInfo.initData(saInfo, formInfo)
  saInfo.initInfo(saInfo)

  return saInfo
}