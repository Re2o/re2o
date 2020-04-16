/** This makes an checkbox toggle the appeareance of the
 * password and password confirmations fields.
 */
function toggle_show_password_chkbox() {
    var password1 = document.getElementById('id_Adherent-password1');
    var password2 = document.getElementById('id_Adherent-password2');

    if (show_password_chkbox.checked) {
    	password1.parentElement.style.display = 'none';
    	password2.parentElement.style.display = 'none';
    	password1.required = false;
    	password2.required = false;
    } else {
    	password1.parentElement.style.display = 'block';
    	password2.parentElement.style.display = 'block';
    	password1.required = true;
    	password2.required = true;
    }
}

var show_password_chkbox = document.getElementById('id_Adherent-init_password_by_mail');
show_password_chkbox.onclick = toggle_show_password_chkbox;
toggle_show_password_chkbox();

