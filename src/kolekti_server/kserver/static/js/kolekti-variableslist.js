$(document).ready(function() {
    
    var progressHandlingFunction = function(){}
    
    var path = $('.browser').data('browserpath')
    
    kolekti_browser({
        'root':'/sources/'+kolekti.lang+'/variables',
        'path':path,
		'parent':".browser",
		'title':" ",
		'titleparent':".title",
		'mode':"selectonly",
		'modal':"no",
		'os_actions':'yes',
		'create_actions':'yes'
	}).select(
	    function(path) {
            var lang = path.split('/')[3]
            console.log(path)
            var variable_path = path.split('/').splice(5).join('/')
            variable_path = variable_path.replace('.xml','')
		    document.location.href = Urls.kolekti_variable(kolekti.project, lang, variable_path)
	    })
    	.create(create_varfile) 
	    .setup_file(setup_varfile);

    $('#browser_lang' ).on('click',".upload-varfile", upload_varfile_form)
    $('.doimport').on('click', function(e) {
	    upload_varfile()
	    $('#uploadmodal').modal('hide');
    });
});
