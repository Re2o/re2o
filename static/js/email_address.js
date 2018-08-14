/** To enable the redirection has no meaning if the local email adress is not
 * enabled. Thus this function enable the checkbox if needed and changes its
 * state.
 */
function enable_redirection_chkbox() {
    var redirect = document.getElementById('id_User-local_email_redirect');
    var enabled = document.getElementById('id_User-local_email_enabled').checked;
    if(!enabled)
    {
        redirect.checked = false;
    }
    redirect.disabled = !enabled;
}

var enabled_chkbox = document.getElementById('id_User-local_email_enabled');
enabled_chkbox.onclick = enable_redirection_chkbox;
enable_redirection_chkbox();
