


var update_documents = function(project, release, lang, container, statecell, status ) {
	$.getJSON('/translator/'+project+'/documents/?release=/releases/'+release + "&lang=" + lang)
	    .success(function(data) {
//		    console.log(data)
		    var refresh = false;
            if(container.is(':empty')) {
                $.each(data, function(index, docs) {
                    container.append($('<tr>', {
                        'class':'t'+index,
                        'html':$('<th>', {
                            html:docs[0]
                        })
                    }))
                });
            }

            var can_validate_all = (status == 'validation')
            
            $.each(data, function(index, docs) {
                var row = container.find('tr.t'+index)
                var doclink;
                if(!docs[3]) can_validate_all = false
                if (docs[2]) {
                    var certif_url = "/translator/"+project+'/'+release+'/'+lang + "/certif/";
                    doclink = [$('<a>',{
					    'href':'/translator/' + project +'/'+ docs[1],
                        'title':docs[0],
					    "target":"_documents",
					    'html':$('<i>',{'class':'fa fa-file-pdf-o'})
					}), ' ']
                    
                    if(status == "publication")
                        doclink.push(
                            $("<span>", {
                                "class":"text-success",
                                "html":$("<i>", {
                                    'class': "fa fa-check"
                                })
                            }))
                            
                    if(status == "validation")
                        doclink.push(
                            $('<form>', {
                                "method":"POST",
                                "action":certif_url,
                                "class":"form form-inline",
                                "style":"display:inline",
                                "html":[
                                    $('<a>', {
                                        'title':"Upload certificate ",
                                        'class':"btn btn-xs "+ (docs[3]?"btn-success":"btn-default"),
                                        'html': $("<i>", {
                                            'class': "fa fa-check-square"
                                        })
                                    }).on('click', function(){
                                        $(this).next().click()
                                    }),
                                    $('<input>', {
                                        'type':"file",
                                        'name':"upload_file",
                                        'class':"hidden btn btn-xs btn-default btn-upload-certificate"
                                    }).on('change', function() {
                                        var formdata = new FormData($(this).closest('form')[0])
                                        //        formdata.append('file', this.files[0]);
                                        
                                        $.ajax({
                                            url : certif_url,
                                            data : formdata,
                                            type : 'POST',
                                            processData: false,
                                            contentType: false,
                                        }).done(function(data){
                                            data = JSON.parse(data)
                                            console.log(data)
                                            window.location.reload()
                                        })
                                        
                                        //  $(this).closest('form').submit()
                                        
                                    }),
                                    $('<input>', {
                                        'type':"hidden",
                                        'name':"path",
                                        'value':docs[1]
                                    })
                                    
                                ]
                            })
                        );
                } else {
                    doclink = $("<i>", {
                        'class': "fa fa-question"
                    })
                };
                   
                row.append($('<td>', {
                    html:doclink
                }));
            });

            
            
            $(statecell).append(
                $('<th>',{
                    'html':[
                        $('<span>', {
			                "html":lang
                        }),
                        (!can_validate_all)?"":$('<a>', {
                            'title':"Validate all documents in this language ",
                            'class':"btn btn-xs btn-primary",
                            'style':"margin-left:6px",
                            'html': $("<i>", {
                                'class': "fa fa-check-square"
                            })
                        }).on('click', function(){
                            var url = "/translator/"+project+'/'+release+'/'+lang + "/commit/"
                            $.ajax({
                                url : url,
                                type : 'POST',
                                processData: false,
                                contentType: false,
                            }).done(function(data){
                                data = JSON.parse(data)
                                console.log(data)
                                window.location.reload()
                            })
                        })
                    ]
		        })
            )

	    })
};



var update_releases_langs = function(release) {
    console.log('update_releases_langs', release)
    var sourcelang,
	    releasepath = release.data('release'),
	    project = release.data('project'),
	    statecell = release.find('.kolekti-release-langs'),
        documentscell = release.find('.kolekti-release-documents');
    

    statecell.html("<td></td>")
    documentscell.html("")
    $.getJSON('/translator/'+project+'/release/states/?release=/releases/'+releasepath)
	    .success(function(data) {
	        $.each(data, function(index,item) {
		        var i = item[0]
		        var v = item[1]
                
		        if (v == 'sourcelang' || v == "translation" || v == "validation" || v == "publication" ) {
                    update_documents(project, releasepath, i, documentscell, statecell, v);
                }
            });
	    });
};

var republish_documents = function(project, release, lang, callbacks){
    $.get('/translator/'+project+'/publish/?release=/releases/'+release  + "&lang=" + lang)
	    .success(function(data) {
            callbacks.hasOwnProperty('success') && callbacks['success'](data)
	    })
        .error(function(x,e) {
            callbacks.hasOwnProperty('error') && callbacks['error']()
        })
	    .always(function() {
            callbacks.hasOwnProperty('always') && callbacks['always']()
	    })
}

$(function() {    
    $('.release').each(function(){
	    update_releases_langs($(this))
    });

    
    $('.upload-assembly-form').on('submit', function(e) {
        console.log("upload", this)
        e.preventDefault()
        $('#uploadStatusModal .upload-status').html('')
        $('#uploadStatusModal').modal()
        $('#uploadStatusModal .upload-progress').show()
        $('#uploadStatusModal .upload-progress .progresstxt').html("Uploading...")
        var formdata = new FormData($(this)[0])
//        formdata.append('file', this.files[0]);
        
        $.ajax({
            url : '/translator/upload/',
            data : formdata,
            type : 'POST',
            processData: false,
            contentType: false,
        }).done(function(data){
            data = JSON.parse(data)
            console.log(data)
            
            if (data.status == 'success') {
                $('#uploadStatusModal .upload-status').html(
                    $('<div>', {
                        'class':'alert alert-success',
                        'html':$('<div>', {
                            'class':'alert-content',
                            'html':data.message
                        })
                    })
                )
                $('#uploadStatusModal .upload-progress .progresstxt').html("Publishing...")
                republish_documents(data.info.project, data.info.release, data.info.lang, {
                    'success': function(pdata) {
                        $('#uploadStatusModal .upload-progress').hide()
                        console.log(pdata)
                        var release_elt = $('.release')
                        $('#uploadStatusModal .upload-status').append(
                            $('<div>', {
                                'class':'alert alert-success',
                                'html':$('<div>', {
                                    'class':'alert-content',
                                    'html':"publication sucessful"
                                })
                            })
                        )
//            	        update_documents(data.info.project, data.info.release, data.info.lang)
                    }
                })

            } else {
                $('#uploadStatusModal .upload-progress').hide()
                $('#uploadStatusModal .upload-status').html(
                    $('<div>', {
                        'class':'alert alert-danger',
                        'html':$('<div>', {
                            'class':'alert-content',
                            'html':data.message
                        })
                    })
                )
            }
        }).error(function() {
            $('#uploadStatusModal .upload-progress').hide()
            $('#uploadStatusModal .upload-status').html(
                $('<div>', {
                    'class':'alert alert-danger',
                    'html':$('<div>', {
                        'class':'alert-content',
                        'html':'an unexpected error occured'
                    })
                })
            )
            
        }).always(function() {

        })
        
        return true;
    })

    $('#uploadStatusModal').on('hidden.bs.modal', function() {
        window.location.reload()
    })
    
    $('body').on('click','.releaselang', function(e) {
        e.preventDefault()
        e.stopPropagation()
	    var releaseo = $(this).closest('.release')
        var release = $(releaseo).data('release')
	    var project = $(releaseo).data('project')
	    var lang = $(this).data('lang')
	    $(releaseo).data('lang',lang)
	    var statecell = $(this).closest('.kolekti-release-langs')
	    var documentcell = $(releaseo).find('.kolekti-release-documents')
        update_documents(project, release, lang, documentcell)
	    statecell.find('span').removeClass('active')
	    statecell.find('.lg-'+lang).addClass('active')
    })
	
    $('body').on('click','.republish', function() {
        var release_elt = $(this).closest('.release');
        var project = release_elt.data('project')
        var release = release_elt.data('release')
        var lang = release_elt.data('lang')
        var documentcell = release_elt.find('.kolekti-release-documents')
        console.log('republish', project, release, lang, documentcell)
        republish_documents(release_elt, {
            'success': function() {
            	update_documents(project, release, lang, documentcell)
            }
        })
    })

    
    $('body').on('click','.commit', function() {
	var release = $(this).closest('.release').data('release')
	var project = $(this).closest('.release').data('project')
	var documentcell = $(this).closest('.release').find('.kolekti-release-documents')
	var lang = $(this).closest('.release').data('lang')
	$(this).closest('.release').find('.processing-commit').removeClass('hidden')
	$(this).closest('.release').find('.commit').addClass('hidden')
	$.post('/translator/'+project+'/' + release + '/' + lang +'/commit/')
	    .success(function(data) {
		update_documents(project, release, lang, documentcell)
	    })
	    .always(function() {
		$(this).closest('.release').find('.commit').removeClass('hidden')
		$(this).closest('.release').find('.processing-commit').addClass('hidden')
	    })		
    })

    $('#downloadModal,#uploadModal').on('show.bs.modal', function (event) {
	var button = $(event.relatedTarget) // Button that triggered the modal
        var release = $(button).closest('.release')
        var source_assembly_url = $(release).data('source-assembly-url')
        var source_zip_url = $(release).data('source-zip-url')
        var upload_url = $(release).data('upload-url')
        var sourcelang = $(release).data('sourcelang')
        var lang = $(release).data('lang')
        var modal = $(this)
//        console.log($(release).data('translated'))
        if ((lang != $(release).data('sourcelang')) && $(release).data('translated'))
            modal.find('.translations').show()
        else
            modal.find('.translations').hide()
        modal.find('form').data('release',release.data('release'))
        modal.find('form').data('project',release.data('project'))
        modal.find('.langtext').text(lang)
        modal.find('.langinput').attr('value',lang)
        modal.find('.sourcelangtext').text(sourcelang)
        modal.find('.link-source.source.zip').attr('href', source_zip_url + "?lang=" + sourcelang)
        modal.find('.link-source.source.assembly').attr('href', source_assembly_url + "?lang=" + sourcelang)
        modal.find('.link-source.current.zip').attr('href', source_zip_url + "?lang=" + lang)
        modal.find('.link-source.current.assembly').attr('href', source_assembly_url + "?lang=" + lang)
        modal.find('form.form-upload-translation').attr('action', upload_url) 
    })
})
