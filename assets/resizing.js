/* resize figures in table upon callback get fires */

if(!window.dash_clientside) {window.dash_clientside = {};}
window.dash_clientside.clientside = {
   resize: function (value) {
       console.log("resizing...");
       window.dispatchEvent(new Event('resize'));
       return null
   }
}

$(document).ready(function(){   
    setTimeout(function () {
        $("#cookieConsent").fadeIn(200);
     }, 4000);
    $("#closeCookieConsent, .cookieConsentOK").click(function() {
        $("#cookieConsent").fadeOut(200);
    }); 
});