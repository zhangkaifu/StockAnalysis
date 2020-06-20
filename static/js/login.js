/**
 * Created by Administrator on 2019/12/21.
 */
function UnameVerification(username){
    console.log(username);
    var inpObj = document.getElementById("username");
    if(inpObj.checkValidity() == false){
        inpObj.setCustomValidity("请重新输入数值（100~300之间）!");


        document.getElementById("userValid").innerHTML = inpObj.validationMessage;
    }
    // if(isName(username)){
    //
    // }else{
    //     alert("用户名格式不对，只可以为大小写的字母");
    // }
}
function UpasswordVerification(password) {

}

//用户名验证
function isName(str) {
    var regExp = new RegExp('[a-zA-Z\-]*$/g');
    var result = regExp.exec(str);
    if (result == null) {
        return false;
    } else {
        return result;
    }
  }