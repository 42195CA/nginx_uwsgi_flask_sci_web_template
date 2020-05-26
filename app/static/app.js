//doc.ready()
// init page or after clicking step_1 tab 
function initStep_1() {
	$("a[data-toggle='pill']").addClass('disabled');
	$("button[ data-toggle='collapse']").addClass('disabled');

	$('#step_2_content_table').find('table').remove();
	$('#programlist_multiselect').empty();

	$("#programsummary td").parent().remove();
	
	$('#predictplotZone').find('img').remove();
    	$('#plotZone').find('img').remove();
    
  	$("#title").val('C1000 vs MIS');
	$("#xlabel").val('MIS');  
	$("#ylabel").val('C1000');  
    	$("#titlesize").val('15');
    	$("#labelsize").val('12');
    	$("#legendsize").val('10');   
    	$("#linewidth").val('1');
    	$("#markdersize").val('4');
    	$("#xtick").val('1,2,5,10,20,36,50,100,180');
    	$("#ytick").val('0.1,0.2,0.5,1,2,5,10,20,50,100,200,500,1000');
        $("#plotOptions").collapse("hide");
        $("#inputestX").val('36')
	$("#xtickrotation").val('0');

}



function updateTableHeader(replacements){
   $("#programsummary th").each(function() {
    var $this = $(this);
    var ih = $this.html();
    $.each(replacements, function(index, value) {
      ih = ih.replace(value[0], value[1]);
    });
    $this.html(ih);
  });
  

}      

function check_inputdata(){
    p1 = parseFloat($('#inputestX').val());
    if (isNaN(p1) || p1 === 0) {
        //alert("Estimated Input cannot more than EMPTY or ZERO");
        $('#inputestX').focus();
        return;
    }
}


function initData_afterUpload(data) {
    $("a[data-toggle='pill']").removeClass('disabled');
    
	var datatable = data['datatable']
	var programlist = data['programlist'];
	// init data table for reivew
	$('#v-pills-tab a[href="#step_2_content"]').tab('show')
	//$("#step_2").show();
	$('#step_2_content_table').find('table').remove();
	$("#step_2_content_table").append(datatable);
	// init program list for plot
	$('#programlist_multiselect').empty();
	$.each(programlist, function (key, value) {
    	    console.log(key,value)
		//$('#programlist_multiselect').append($("<option></option>").attr("value",value).text(value));
		$("#programlist_multiselect").append($('<option>', {
           value: value
          ,text: value
          ,selected: 'selected'
        }));
	});        
    
	$('#programlist_multiselect').multiselect('rebuild');
	// init program data for predict
	$("#showdatatype").text(data['datatype']);
	$("#programsummary td").parent().remove();
	var programdata = data['program'];

	for (i = 0; i < programdata.length; i++) {
		//console.log(pinf[i]);
		var table = document.getElementById("programsummary");
		var row = table.insertRow(-1);
		var pname = programdata[i].name;
		var pmin = programdata[i].minX;
		//        if(data['datatype'].indexOf("MIS")) {pmin=1}
		var pmax = programdata[i].maxX;
		var mid = i;
		//console.log(mid);
		row.id = mid;
		//    alert(pmax);
		var cell0 = row.insertCell(0);
		var cell1 = row.insertCell(1);
		var cell2 = row.insertCell(2);
		var cell3 = row.insertCell(3);
		var cell4 = row.insertCell(4);
		var cell5 = row.insertCell(5);
		var cell6 = row.insertCell(6);
                var cell7 = row.insertCell(7);
		cell0.innerHTML = "<input type='checkbox' checked='checked' class='checkProgram' id='checkProgram_" + mid + "' style='width:20px'> </input>";
		cell1.innerHTML = "<input type='text'  disabled=true class='pname' id='pname_" + mid +	"' value='" + pname + "' style='width:120px' readonly> </input>";
		cell2.innerHTML = "<input type='text'   class='minX userinput' id='minX_" + mid + 	"' value='" + pmin + "' style='width:60px'> </input>";
		cell3.innerHTML = "<input type='text'   class='maxX userinput' id='maxX_" + mid + 	"' value='" + pmax + "' style='width:60px'> </input>";
		cell4.innerHTML = "<input type='text'   disabled=true class='estX' id='estX_" + 	mid + "' value='" + $("#inputestX").val() +"' style='width:60px' readonly> </input>";
		cell5.innerHTML = "<input type='text'   disabled=true class='estY' id='estY_" + 	mid + "' value=' ' style='width:60px' readonly> </input>";
		cell6.innerHTML = "<input type='text'   disabled=true class='slope' id='slope_" + mid + "' value=' ' style='width:60px' readonly> </input>";
                cell7.innerHTML = "<input type='text'   disabled=true class='lambda' id='lambda_" + mid + "' value=' ' style='width:60px' readonly> </input>";
	} // END FOR   
	
	//update header


	updateTableHeader([["Start X", "Start "+ data['data_x_name']]]);
	updateTableHeader([["End X", "End "+ data['data_x_name']]]);
    	updateTableHeader([["1", "Estimated "+ data['data_x_name']]]);
	updateTableHeader([["2", "Estimated "+ data['data_y_name']]]);


	//initial plot options
	 fname=data['filename']
	 fname=fname.split('.')[0]
	 $("#title").val(fname);
 
	 $("#xlabel").val(data['data_x_name']);
	 $("#ylabel").val(data['data_y_name']);
         $("#xtick").val(data['xtick'])
	 $("#show_data_x_name").val(data['data_x_name']);
	 $("#show_data_y_name").val(data['data_y_name']);
	 $("#inputestX").val(data['inputEstX']);
         $('.estX').val(data['inputEstX'])


} // END FUNCTION



function uploadFile() {
	$.ajax({
		url: "/upload",
		type: 'POST',
		data: new FormData($("#upload-file-form")[0]),
		cache: false,
		processData: false,
		contentType: false,
		error: function () {
			console.log("upload error");
		},
		success: function (data) {
			console.log(data);
			console.log(data['data']);
			initStep_1();
			initData_afterUpload(data['data']);
		} // end success
	}); // end ajax
} // end function


function downloadFile(task){
    var table = document.getElementById("programsummary");
    var rows = table.rows; // or table.getElementsByTagName("tr");
    var trl = rows.length - 1; //body line
    var x=$("#show_data_x_name").val();
    var y=$("#show_data_y_name").val();
    var csv = 'Program\tFitting_Start_'+x+'\tFitting_End_'+x+'\tPredict_'+x+'\tPredicted_'+y+'\tSlope\tLambda\n'
    for (i = 0; i < trl; i++) {
        var pname = $("#pname_" + i).val();
	if ($("#checkProgram_" + i).prop('checked')) {
            var pminX = $("#minX_" + i).val()
            var pmaxX = $("#maxX_" + i).val()
            var pestX = $("#estX_" + i).val()
            var pestY = $("#estY_" + i).val()
            var pslope = $("#slope_" + i).val()
            var plambda = $("#lambda_" + i).val()
            csv += pname +'\t'+ pminX +'\t'+ pmaxX +'\t' + pestX +'\t'+ pestY +'\t'+ pslope +'\t'+ plambda + '\n';
        }
    }
    csv = csv.replace(/\n$/, "")
    var fileName= "result.csv";
    var pp = document.createElement('a');
    pp.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURI(csv));
    pp.setAttribute('download', fileName);
    pp.click();
	
} // end downloadFile


function plotFile(task) {
	// collect model and task type data  
	var estX = parseFloat($("#inputestX").val());
 	// var estX=$("#estX_0").val();
	var plotinfor = {
		"xtick": $("#xtick").val(),
		"ytick": $("#ytick").val(),
		"titlesize": $("#titlesize").val(),
		"legendsize": $("#legendsize").val(),
		"labelsize": $("#labelsize").val(),
		"title": $("#title").val(),
		"xlabel": $("#xlabel").val(),
		"ylabel": $("#ylabel").val(),
		"legendposition": $("#legendposition").val(),
		"linewidth": $("#linewidth").val(),
		"markdersize": $("#markdersize").val(),
		"xtickrotation": $("#xtickrotation").val()
	};
	
	if (task == 'plot') {
		programinfor = $('#programlist_multiselect').val();
		estX = 0
		// preapre all the plot function parameters
	} else {
		var table = document.getElementById("programsummary");
		var rows = table.rows; // or table.getElementsByTagName("tr");
		var trl = rows.length - 1; //body line
		var programinfor = {};
		for (i = 0; i < trl; i++) {
			var pname = $("#pname_" + i).val();
			var psel = 0;
			if ($("#checkProgram_" + i).prop('checked')) {
				psel = 1;
			}
			var pminX = parseFloat($("#minX_" + i).val());
			var pmaxX = parseFloat($("#maxX_" + i).val());
			//var tp = {selected:psel,minX:pminX,maxX:pmaxX}
			var tp = {
				pid: i,
				selected: psel,
				minX: pminX,
				maxX: pmaxX
			}
			programinfor[pname] = tp;
			//check_inputdata();
		}
	}
	var plotfunctionparameters = {
		"task": task
		,"estX": estX
		,"plot": plotinfor
		,"program": programinfor
	};

	$.ajax({
		url: "plot",
		type: 'POST',
		data: JSON.stringify(plotfunctionparameters),
		dataType: "json",
		contentType: "application/json",
		error: function () {
			alert("plot error! Please modfiy parameters and try again.");
			if (task == 'plot') {
				$('#plotZone').find('img').remove();
			}
            else {
                 $('#predictplotZone').find('img').remove();
            }
		},
		success: function (data) {
			var plots = data['data']['plotimg'];
			if (task == 'plot') {
				$('#plotZone').find('img').remove();
				var img = $('<img />').attr({
					'id': 'weibullplot',
					'src': 'data:image/jpeg;base64,' + plots,
					'alt': 'weibull',
					'title': 'c1000',
					'width': 800
				}).appendTo('#plotZone');
			} // end if
			else {
				$('#predictplotZone').find('img').remove();
				var img = $('<img />').attr({
					'id': 'weibullplot',
					'src': 'data:image/jpeg;base64,' + plots,
					'alt': 'weibull',
					'title': 'c1000',
					'width': 800
				}).appendTo('#predictplotZone');
				
				var calvalue = data['data']['calvalue']
				$('.estY').val('');
				$('.slope').val('');
                                $('.lambda').val('');
				for (var i in calvalue) {
					pval = calvalue[i];
					$("#estY_" + i).val(pval['estY']);
					$("#slope_" + i).val(pval['beta']);
                                        $("#lambda_" + i).val(pval['lambda']);
				} // end for
			} // end if else        
		} // end success
	}); // end ajax
} // end function plot


$(document).ready(function () {
    	initStep_1();
    
    	$("#step_1, #step_2").click(function () {
		$("button[ data-toggle='collapse']").addClass('disabled');
		$("#plotOptions").collapse("hide");
	});
    
	$("#clickstep3button").click(function () {
		$("button[ data-toggle='collapse']").removeClass('disabled');
		$('#v-pills-tab a[href="#step_3_content"]').tab('show')
		plotFile("plot");
	});


	$("#step_3").click(function () {
		$("button[ data-toggle='collapse']").removeClass('disabled');
		plotFile("plot");
	});

	$("#step_4").click(function () {
		$("button[ data-toggle='collapse']").removeClass('disabled');
		plotFile("predict");
	});	
	
	
	$('input:file').on("change", function () {
        	if ($("input:file").val() == "") {
            		return;
        }
		uploadFile();
	});
	
	$('input:file').on("click", function () { initStep_1();});   
	
	
	$("#plot,#predict").click(function () {plotFile($(this).attr('id'));	});
	
	
	$("#inputestX").on("keypress keyup blur", function (event) {
        $(this).val($(this).val().replace(/[^0-9\.]/g, ''));
    	if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {		event.preventDefault();}
    	$('.estX').val($("#inputestX").val());
    });	
	
    $('#programsummary').on('focusout', '.minX , .maxX', function (event) {
        var tid = $(this).attr('id');
        var xid = tid.substring(5, tid.length);
        
        if ($("#checkProgram_" + xid).prop('checked')) {            
            var texta = '#minX_' + xid;
            var textb = '#maxX_' + xid;
            var va = parseFloat($(texta).val());
            var vb = parseFloat($(textb).val());
            if (isNaN(vb) || isNaN(va) ) {
                //alert('min and max can not be empty!');
                $(this).focus();
            }
            
            if (va >= vb || va <= 0) {
                //alert('minX should be less than maxX!');
                $(texta).focus();
            }
           }
    });


    $('#programsummary').on('keypress', '.minX,.maxX', function (event) {
    	if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {		
        	event.preventDefault();
        	}
    });

    $("#download").on("click", function () { downloadFile();});
  
	
})
