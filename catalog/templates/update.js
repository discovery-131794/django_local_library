var data = {
    model: 'category.emailaddress',
    pk: 'zhang',
    fields: {
        address: 'discovery131794@163.com',
        role: 'requestor'
    }
}
var record = JSON.stringify(data)

let xhr = new XMLHttpRequest();
let url = 'http://127.0.0.1:8000/category/update/'
xhr.open('POST', url);
xhr.onload = function(){
    if(xhr.status===200){
        alert('添加成功');
    }
}
xhr.send(record)