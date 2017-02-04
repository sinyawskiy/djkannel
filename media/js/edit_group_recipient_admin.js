var SMSAdmin;
if(!SMSAdmin) SMSAdmin={};

(function($) {
    function randomString(length) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');

    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }

    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
    }

    $(document).ready(function() {
        var field = $('#id_password');
        field.after('&nbsp;<a class="create_new_password" href="javascript:void();">Создать новый пароль</a>&nbsp;<a class="clear_password" href="javascript:void();">Убрать пароль</a>');
        field.parent().find('a.create_new_password').click(function(){
            field.val(randomString(10));
        });
        field.parent().find('a.clear_password').click(function(){
            field.val('');
        });

    });
})(django.jQuery);

