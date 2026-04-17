export const adaptSxsList = (response) => {
  if (!response || !response.object_list) {
    return { columns: [], data: [] }
  }

  const columns = [
    { label: '名称', prop: 'sxsname', minWidth: '150', show: true },
    { label: '门牌号', prop: 'sxsno', minWidth: '120', show: true },
    { label: '设备数量', prop: 'device_count', minWidth: '100', show: true },
    { label: '课程数', prop: 'course_count', minWidth: '100', show: true },
    { label: '管理员', prop: 'admin_name', minWidth: '120', show: true },
    { label: '所属系部', prop: 'depart_name', minWidth: '150', show: true },
    { label: '备注', prop: 'sxsmemo', minWidth: '200', show: true },
    { label: '操作', prop: 'actions', minWidth: '200', show: true, isAction: true }
  ]

  const rawRows = response.object_list
  const qtype = response.qtype

  const data = rawRows.map(row => {
    const actions = [
      {
        text: '编辑',
        action_type: 'edit',
        resource_type: 'sxs',
        resource_id: row.id,
        context: { opttype: 1 },
        style_class: 'btn-primary-sm'
      }
    ]

    if (qtype == 4 || qtype === '4') {
        actions.push({
            text: '删除',
            action_type: 'delete',
            resource_type: 'sxs',
            resource_id: row.id,
            style_class: 'btn-danger-sm',
            onclick: '确定要删除这个实训室吗？'
        })
    }

    return {
      id: row.id,
      sxsname: row.sxsname,
      sxsno: row.sxsno,
      device_count: row.device_count || 0,
      course_count: row.course_count || 0,
      admin_name: row.admin_name || '未分配',
      depart_name: row.depart_name || '',
      sxsmemo: row.sxsmemo || '',
      actions: actions
    }
  })
  
  return { 
    columns, 
    data,
    page_obj: response.page_obj,
    paginator: response.paginator,
    is_paginated: response.is_paginated
  }
}

export const adaptDeptList = (response) => {
  if (!response) {
    return { columns: [], data: [] }
  }

  const rawRows = response.object_list || (Array.isArray(response) ? response : [])
  
  const columns = [
    { label: '分院名称', prop: 'departname', minWidth: '150', show: true },
    { label: '备注', prop: 'departdemo', minWidth: '200', show: true },
    { label: '用户数', prop: 'user_count', minWidth: '100', show: true },
    { label: '操作', prop: 'actions', minWidth: '150', show: true, isAction: true }
  ]

  const data = rawRows.map(row => {
      if (!Array.isArray(row)) {
          const actions = [
              {
                  text: '编辑',
                  action_type: 'edit',
                  resource_type: 'dept',
                  resource_id: row.id,
                  style_class: 'btn-primary-sm'
              },
              {
                  text: '删除',
                  action_type: 'delete',
                  resource_type: 'dept',
                  resource_id: row.id,
                  style_class: 'btn-danger-sm',
                  onclick: '确定要删除这个分院吗？'
              }
          ]

          return {
              id: row.id,
              departname: row.departname,
              departdemo: row.departdemo || '-',
              user_count: row.user_count || 0,
              actions: actions
          }
      } else {
          return {
              id: row[0],
              departname: row[1],
              departdemo: row[2],
              actions: []
          }
      }
  })
  
  return { 
    columns, 
    data,
    page_obj: response.page_obj,
    paginator: response.paginator,
    is_paginated: response.is_paginated
  }
}

export const adaptUserList = (response) => {
  if (!response || !response.object_list) {
    return { columns: [], data: [] }
  }

  const columns = [
    { label: '用户名', prop: 'username', minWidth: '120', show: true },
    { label: '邮箱', prop: 'email', minWidth: '180', show: true },
    { label: '手机号', prop: 'phone', minWidth: '120', show: true },
    { label: '昵称', prop: 'nikename', minWidth: '120', show: true },
    { label: '角色', prop: 'role_name', minWidth: '120', show: true },
    { label: '操作', prop: 'actions', minWidth: '200', show: true, isAction: true }
  ]
  
  const firstItem = response.object_list[0]
  if (firstItem && firstItem.depart_name) {
      columns.splice(5, 0, { label: '部门', prop: 'depart_name', minWidth: '150', show: true })
  }

  const rawRows = response.object_list
  const qtype = response.typeid

  const data = rawRows.map(row => {
    const actions = []
    
    actions.push({
        text: row.is_active ? '禁用' : '激活',
        action_type: 'activate',
        resource_type: 'user',
        resource_id: row.id,
        style_class: row.is_active ? 'btn-primary-sm' : 'btn-success-sm'
    })
    
    actions.push({
        text: '分配角色',
        action_type: 'edit',
        resource_type: 'user_role',
        resource_id: row.id,
        context: { tid: qtype },
        style_class: 'btn-primary-sm'
    })

    const userType = row.user_type ?? 0
    const hasPermission = (perm) => (userType & perm) !== 0

    return {
      id: row.id,
      username: row.username,
      email: row.email || '',
      phone: row.phone || '',
      nikename: row.nikename || '',
      role_name: row.role_name || '',
      depart_name: row.depart_name || '',
      is_superuser: row.is_superuser || row.is_super || false,
      is_departadmin: hasPermission(4),
      is_sxsadmin: hasPermission(2),
      is_teacher: hasPermission(1),
      managed_sxs: row.managed_sxs || '',
      user_type: userType,
      actions: actions
    }
  })
  
  return { 
    columns, 
    data,
    page_obj: response.page_obj,
    paginator: response.paginator,
    is_paginated: response.is_paginated
  }
}

export const adaptRecordList = (response) => {
  if (!response) {
    return { columns: [], data: [] }
  }

  let rawHeaders = []
  let rawRows = []

  if (Array.isArray(response)) {
      if (response.length > 0 && Array.isArray(response[0])) {
          rawHeaders = response[0]
          rawRows = response.slice(1)
      } else {
          rawRows = response
      }
  } else if (response.items && Array.isArray(response.items)) {
      return adaptItemsFormat(response)
  } else {
      rawHeaders = response.headlist || response.headerlist || []
      if (rawHeaders.length === 0 && response.fields) {
          rawHeaders = response.fields
      }
      rawRows = response.object_list || []
  }

  const headerStr = rawHeaders.join(',')
  const listHeader = response.listheader || ''
  
  const isUsage = headerStr.includes('使用日期') || listHeader.includes('使用记录')
  const isFault = headerStr.includes('故障') || listHeader.includes('故障工单')
  const isMaintain = headerStr.includes('维护内容') || listHeader.includes('维护记录')
  const isArchivedRecords = listHeader.includes('归档记录')

  const columns = []
  
  if (isArchivedRecords && !isUsage && !isFault && !isMaintain) {
      columns.push(
          { label: '类型', prop: 'type', minWidth: '80', show: true },
          { label: 'ID', prop: 'id', minWidth: '80', show: true },
          { label: '实训室', prop: 'sxsname', minWidth: '150', show: true },
          { label: '内容', prop: 'content', minWidth: '200', show: true },
          { label: '日期', prop: 'date', minWidth: '120', show: true }
      )
  } else if (isUsage) {
      columns.push(
          { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
          { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
          { label: '使用日期', prop: 'sxsdate', minWidth: '120', show: true },
          { label: '开始节', prop: 'sxsstart', minWidth: '80', show: true },
          { label: '学时', prop: 'sxsclasshour', minWidth: '80', show: true },
          { label: '上课班级', prop: 'sxsclass', minWidth: '120', show: true },
          { label: '人数', prop: 'sxsnum', minWidth: '80', show: true },
          { label: '授课教师', prop: 'sxsteacher_name', minWidth: '100', show: true },
          { label: '实训内容', prop: 'sxscontent', minWidth: '200', show: true },
          { label: '设备状态', prop: 'sxsdevice_status', minWidth: '100', show: true },
          { label: '实训室状态', prop: 'sxs_status', minWidth: '100', show: true },
          { label: '备注', prop: 'sxsmemo', minWidth: '150', show: true }
      )
  } else if (isFault) {
      columns.push(
          { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
          { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
          { label: '报修时间', prop: 'maintainrequestdate', minWidth: '120', show: true },
          { label: '报修人', prop: 'maintainrequester_name', minWidth: '100', show: true },
          { label: '故障内容', prop: 'maintainrecordcontent', minWidth: '200', show: true },
          { label: '是否已维修', prop: 'ismaintaind', minWidth: '100', show: true },
          { label: '维护人', prop: 'maintainrecordperson_name', minWidth: '100', show: true },
          { label: '备注', prop: 'maintainrecordmemo', minWidth: '150', show: true }
      )
  } else if (isMaintain) {
      columns.push(
          { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
          { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
          { label: '申请日期', prop: 'maintainrequestdate', minWidth: '120', show: true },
          { label: '申请人', prop: 'maintainrequester_name', minWidth: '100', show: true },
          { label: '维护内容', prop: 'maintainrecordcontent', minWidth: '200', show: true },
          { label: '维护日期', prop: 'maintainrecorddate', minWidth: '120', show: true },
          { label: '是否已维护', prop: 'ismaintaind', minWidth: '100', show: true },
          { label: '维护类型', prop: 'maintaintype', minWidth: '100', show: true },
          { label: '维护人', prop: 'maintainrecordperson_name', minWidth: '100', show: true },
          { label: '备注', prop: 'maintainrecordmemo', minWidth: '150', show: true }
      )
  } else if (rawHeaders.length > 0) {
      rawHeaders.forEach((h, i) => {
          if (h === '选择') return 
          columns.push({
              label: h,
              prop: `col_${i}`,
              minWidth: (h === '备注' || h === '内容' || h === '故障内容' || h === '维护内容') ? '200' : '120',
              show: true,
              isAction: h === '操作'
          })
      })
  } else {
      columns.push(
          { label: '内容', prop: 'content', minWidth: '200' },
          { label: '操作', prop: 'actions', minWidth: '150', isAction: true }
      )
  }

  const data = rawRows.map((row, rowIndex) => {
      const item = { id: row[0], _raw: row }
      
      if (isArchivedRecords && !isUsage && !isFault && !isMaintain) {
          item.type = row[0] || ''
          item.id = row[1] || row[0] || ''
          item.sxsname = row[2] || ''
          item.content = row[3] || ''
          item.date = row[4] || ''
      } else if (isUsage || isFault || isMaintain) {
          const getVal = (keywords) => {
              const idx = rawHeaders.findIndex(h => keywords.some(k => h && h.includes(k)))
              return (idx > -1 && idx < row.length) ? row[idx] : ''
          }
          
          if (isUsage) {
              item.sxsname = getVal(['实训室名称', '名称'])
              item.sxsno = getVal(['门牌号'])
              item.sxsdate = getVal(['使用日期', '日期'])
              item.sxsstart = getVal(['开始节', '节次'])
              item.sxsclasshour = getVal(['学时'])
              item.sxsclass = getVal(['上课班级', '班级'])
              item.sxsnum = getVal(['人数'])
              item.sxsteacher_name = getVal(['授课教师', '教师'])
              item.sxscontent = getVal(['实训内容', '内容'])
              item.sxsdevice_status = getVal(['设备状态'])
              item.sxs_status = getVal(['实训室状态'])
              item.sxsmemo = getVal(['备注'])
          } else if (isFault) {
              item.sxsname = getVal(['实训室名称', '名称'])
              item.sxsno = getVal(['门牌号'])
              item.maintainrequestdate = getVal(['报修时间', '申请日期'])
              item.maintainrequester_name = getVal(['报修人', '申请人'])
              item.maintainrecordcontent = getVal(['故障内容', '内容'])
              item.ismaintaind = getVal(['是否已维修', '是否已维护'])
              item.maintainrecordperson_name = getVal(['维护人'])
              item.maintainrecordmemo = getVal(['备注'])
          } else if (isMaintain) {
              item.sxsname = getVal(['实训室名称', '名称'])
              item.sxsno = getVal(['门牌号'])
              item.maintainrequestdate = getVal(['申请日期'])
              item.maintainrequester_name = getVal(['申请人'])
              item.maintainrecordcontent = getVal(['维护内容', '内容'])
              item.maintainrecorddate = getVal(['维护日期'])
              item.ismaintaind = getVal(['是否已维护'])
              item.maintaintype = getVal(['维护类型', '类型'])
              item.maintainrecordperson_name = getVal(['维护人'])
              item.maintainrecordmemo = getVal(['备注'])
          }
      } else {
          columns.forEach((col, colIndex) => {
              const headerIndex = rawHeaders.indexOf(col.label)
              if (headerIndex > -1 && headerIndex < row.length) {
                  item[col.prop] = row[headerIndex]
              }
          })
      }
      
      if (!item.id && row.length > 0) item.id = row[0]

      return item
  })

  return { 
    columns, 
    data,
    page_obj: response.page_obj,
    paginator: response.paginator,
    is_paginated: response.is_paginated
  }
}

function adaptItemsFormat(response) {
  const items = response.items || []
  if (items.length === 0) {
    return { columns: [], data: [] }
  }

  const firstItem = items[0]
  
  if (Array.isArray(firstItem)) {
    const rawHeaders = firstItem
    const rawRows = items.slice(1)
    
    const headerStr = rawHeaders.join(',')
    const listHeader = response.listheader || ''
    
    const isUsage = headerStr.includes('使用日期') || listHeader.includes('使用记录')
    const isFault = headerStr.includes('故障') || listHeader.includes('故障工单')
    const isMaintain = headerStr.includes('维护内容') || listHeader.includes('维护记录')
    
    let columns = []
    
    if (isUsage) {
      columns = [
        { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
        { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
        { label: '使用日期', prop: 'sxsdate', minWidth: '120', show: true },
        { label: '开始节', prop: 'sxsstart', minWidth: '80', show: true },
        { label: '学时', prop: 'sxsclasshour', minWidth: '80', show: true },
        { label: '上课班级', prop: 'sxsclass', minWidth: '120', show: true },
        { label: '人数', prop: 'sxsnum', minWidth: '80', show: true },
        { label: '授课教师', prop: 'sxsteacher_name', minWidth: '100', show: true },
        { label: '实训内容', prop: 'sxscontent', minWidth: '200', show: true },
        { label: '设备状态', prop: 'sxsdevice_status', minWidth: '100', show: true },
        { label: '实训室状态', prop: 'sxs_status', minWidth: '100', show: true },
        { label: '备注', prop: 'sxsmemo', minWidth: '150', show: true }
      ]
    } else if (isFault) {
      columns = [
        { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
        { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
        { label: '报修时间', prop: 'maintainrequestdate', minWidth: '120', show: true },
        { label: '报修人', prop: 'maintainrequester_name', minWidth: '100', show: true },
        { label: '故障内容', prop: 'maintainrecordcontent', minWidth: '200', show: true },
        { label: '是否已维修', prop: 'ismaintaind', minWidth: '100', show: true },
        { label: '维护人', prop: 'maintainrecordperson_name', minWidth: '100', show: true },
        { label: '备注', prop: 'maintainrecordmemo', minWidth: '150', show: true }
      ]
    } else if (isMaintain) {
      columns = [
        { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
        { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
        { label: '申请日期', prop: 'maintainrequestdate', minWidth: '120', show: true },
        { label: '申请人', prop: 'maintainrequester_name', minWidth: '100', show: true },
        { label: '维护内容', prop: 'maintainrecordcontent', minWidth: '200', show: true },
        { label: '维护日期', prop: 'maintainrecorddate', minWidth: '120', show: true },
        { label: '是否已维护', prop: 'ismaintaind', minWidth: '100', show: true },
        { label: '维护类型', prop: 'maintaintype', minWidth: '100', show: true },
        { label: '维护人', prop: 'maintainrecordperson_name', minWidth: '100', show: true },
        { label: '备注', prop: 'maintainrecordmemo', minWidth: '150', show: true }
      ]
    } else {
      columns = rawHeaders.map((header, index) => ({
        label: header,
        prop: `col${index}`,
        minWidth: '120',
        show: true
      }))
    }
    
    const data = rawRows.map((row, rowIndex) => {
      const item = { id: rowIndex + 1 }
      columns.forEach((col, colIndex) => {
        item[col.prop] = row[colIndex]
      })
      return item
    })
    
    return { 
      columns, 
      data,
      page_obj: response.page_obj,
      paginator: response.paginator,
      is_paginated: response.is_paginated
    }
  }
  
  const recordType = response.type || detectRecordType(firstItem)
  
  let columns = []
  
  if (recordType === 'usage') {
    columns = [
      { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
      { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
      { label: '使用日期', prop: 'sxsdate', minWidth: '120', show: true },
      { label: '开始节', prop: 'sxsstart', minWidth: '80', show: true },
      { label: '学时', prop: 'sxsclasshour', minWidth: '80', show: true },
      { label: '上课班级', prop: 'sxsclass', minWidth: '120', show: true },
      { label: '人数', prop: 'sxsnum', minWidth: '80', show: true },
      { label: '授课教师', prop: 'sxsteacher_name', minWidth: '100', show: true },
      { label: '实训内容', prop: 'sxscontent', minWidth: '200', show: true },
      { label: '设备状态', prop: 'sxsdevice_status', minWidth: '100', show: true },
      { label: '实训室状态', prop: 'sxs_status', minWidth: '100', show: true },
      { label: '备注', prop: 'sxsmemo', minWidth: '150', show: true }
    ]
  } else if (recordType === 'fault') {
    columns = [
      { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
      { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
      { label: '报修时间', prop: 'maintainrequestdate', minWidth: '120', show: true },
      { label: '报修人', prop: 'maintainrequester_name', minWidth: '100', show: true },
      { label: '故障内容', prop: 'maintainrecordcontent', minWidth: '200', show: true },
      { label: '是否已维修', prop: 'ismaintaind', minWidth: '100', show: true },
      { label: '维护人', prop: 'maintainrecordperson_name', minWidth: '100', show: true },
      { label: '备注', prop: 'maintainrecordmemo', minWidth: '150', show: true }
    ]
  } else if (recordType === 'maintain') {
    columns = [
      { label: '实训室名称', prop: 'sxsname', minWidth: '150', show: true },
      { label: '门牌号', prop: 'sxsno', minWidth: '100', show: true },
      { label: '申请日期', prop: 'maintainrequestdate', minWidth: '120', show: true },
      { label: '申请人', prop: 'maintainrequester_name', minWidth: '100', show: true },
      { label: '维护内容', prop: 'maintainrecordcontent', minWidth: '200', show: true },
      { label: '维护日期', prop: 'maintainrecorddate', minWidth: '120', show: true },
      { label: '是否已维护', prop: 'ismaintaind', minWidth: '100', show: true },
      { label: '维护类型', prop: 'maintaintype', minWidth: '100', show: true },
      { label: '维护人', prop: 'maintainrecordperson_name', minWidth: '100', show: true },
      { label: '备注', prop: 'maintainrecordmemo', minWidth: '150', show: true }
    ]
  } else {
    columns = Object.keys(firstItem)
      .filter(key => key !== 'id' && !key.endsWith('_id'))
      .map(key => ({
        label: formatFieldLabel(key),
        prop: key,
        minWidth: '120',
        show: true
      }))
  }

  const data = items.map(item => ({
    id: item.id,
    ...item
  }))

  return { 
    columns, 
    data,
    page_obj: response.page_obj,
    paginator: response.paginator,
    is_paginated: response.is_paginated
  }
}

function detectRecordType(item) {
  if (item.sxsdate || item.sxsclasshour || item.sxscontent) {
    return 'usage'
  }
  if (item.maintainrecordcontent && !item.maintaintype) {
    return 'fault'
  }
  if (item.maintainrecordcontent && item.maintaintype) {
    return 'maintain'
  }
  return 'usage'
}

function formatFieldLabel(fieldName) {
  const labelMap = {
    'sxsname': '实训室名称',
    'sxsno': '门牌号',
    'sxsdate': '使用日期',
    'sxsstart': '开始节',
    'sxsclasshour': '学时',
    'sxsclass': '上课班级',
    'sxsnum': '人数',
    'sxsteacher_name': '授课教师',
    'sxscontent': '实训内容',
    'sxsdevice_status': '设备状态',
    'sxs_status': '实训室状态',
    'sxsmemo': '备注',
    'maintainrequestdate': '申请日期',
    'maintainrequester_name': '申请人',
    'maintainrecordcontent': '维护内容',
    'maintainrecorddate': '维护日期',
    'ismaintaind': '是否已维护',
    'maintaintype': '维护类型',
    'maintainrecordperson_name': '维护人',
    'maintainrecordmemo': '备注'
  }
  return labelMap[fieldName] || fieldName
}

export const adaptTermList = (response) => {
  if (!response) {
    return { columns: [], data: [] }
  }

  const rawRows = response.object_list || (Array.isArray(response) ? response : [])
  
  const columns = [
    { label: '学期名称', prop: 'termname', minWidth: '150', show: true },
    { label: '开始日期', prop: 'termstart', minWidth: '120', show: true },
    { label: '结束日期', prop: 'termend', minWidth: '120', show: true },
    { label: '当前学期', prop: 'is_current', minWidth: '100', show: true, isStatus: true }
  ]

  const data = rawRows.map(row => {
    if (!Array.isArray(row)) {
        const actions = [
            {
                text: '编辑',
                action_type: 'edit',
                resource_type: 'term',
                resource_id: row.id,
                style_class: 'btn-primary-sm'
            },
            {
                text: '删除',
                action_type: 'delete',
                resource_type: 'term',
                resource_id: row.id,
                style_class: 'btn-danger-sm',
                onclick: '确定要删除这个学期吗？'
            }
        ]

        let statusInfo = { text: '历史', type: 'warning' }
        if (row.is_current) {
            statusInfo = { text: '当前学期', type: 'success' }
        } else if (row.islocked) {
            statusInfo = { text: '已归档', type: 'info' }
        }

        return {
            id: row.id,
            termname: row.termname,
            termstart: row.termstart,
            termend: row.termend,
            startdate: row.termstart,
            enddate: row.termend,
            is_current: statusInfo,
            iscurrent: row.is_current,
            islocked: row.islocked,
            actions
        }
    } else {
        const item = {
            id: row[0],
            termname: row[1],
            termstart: row[2],
            termend: row[3],
            startdate: row[2],
            enddate: row[3],
            is_current: { text: row[4] ? '是' : '否', type: row[4] ? 'success' : 'info' },
            iscurrent: row[4],
            islocked: row[5]
        }
        return item
    }
  })

  return { 
    columns, 
    data,
    page_obj: response.page_obj,
    paginator: response.paginator,
    is_paginated: response.is_paginated
  }
}
