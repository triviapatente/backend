$(checkPasswords);
function checkPasswords() {
    $("#password, #confirm-password").keyup(checkPasswordInput);
}
function checkPasswordInput() {
    var password = $("#password").val();
    var confirmPassword = $("#confirm-password").val();
    if(password == confirmPassword)
        $("#submit").removeAttr("disabled");
    else
        $("#submit").attr("disabled", true);
}
