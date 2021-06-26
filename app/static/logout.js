// LOGOUT
$('#logoutBtn').on('click', function() {
	sessionStorage.clear();
	$.ajax({
		type: 'GET',
		url: '/logout',
		success: function(){
		    window.location.href = "/";
		}
	});
});