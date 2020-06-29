$(document).on('daPageLoad', function(){
    $('input[type="date"]').each(function(){
	var dateElement = this;
	$(dateElement).hide();
	$(dateElement).attr('type', 'hidden');
	var parentElement = $('<div>');
	var yearElement = $('<select>');
	var monthElement = $('<select>');
	var dayElement = $('<select>');
	var today = new Date();
	var dateEntered;
	if ($(dateElement).val()){
	    var utcDate = new Date($(dateElement).val());
	    dateEntered = new Date(utcDate.getUTCFullYear(), utcDate.getUTCMonth(), utcDate.getUTCDate());
	}
	else{
	    dateEntered = null;
	}
	var opt = $("<option>");
	opt.val("");
	opt.text("--");
	monthElement.append(opt);
	for(var month=0; month < 12; month++){
	    opt = $("<option>");
	    if (month < 9){
		opt.val('0' + (month + 1));
	    }
	    else{
		opt.val(month + 1);
	    }
	    var dt = new Date(1970, month, 1);
	    opt.text(dt.toLocaleString('default', { month: 'long' }));
	    if (dateEntered && month == dateEntered.getMonth()){
		opt.attr('selected', 'selected');
	    }
	    monthElement.append(opt);
	}
	opt = $("<option>");
	opt.val("");
	opt.text("--");
	dayElement.append(opt);
	for(var day=1; day <= 31; day++){
	    var opt = $("<option>");
	    if (day < 10){
		opt.val('0' + (day));
	    }
	    else{
		opt.val(day);
	    }
	    opt.text(day);
	    if (dateEntered && day == dateEntered.getDate()){
		opt.attr('selected', 'selected');
	    }
	    dayElement.append(opt);
	}
	opt = $("<option>");
	opt.val("");
	opt.text("--");
	yearElement.append(opt);
	for(var year=today.getFullYear(); year > today.getFullYear() - 50; year--){
	    opt = $("<option>");
	    opt.val(year);
	    opt.text(year);
	    if (dateEntered && year == dateEntered.getFullYear()){
		opt.attr('selected', 'selected');
	    }
	    yearElement.append(opt);
	}	
	function updateDate(){
	    $(dateElement).val($(yearElement).val() + '-' + $(monthElement).val() + '-' + $(dayElement).val());
	}
	$(dateElement).before(parentElement);
	$(parentElement).append(monthElement);
	$(parentElement).append(dayElement);
	$(parentElement).append(yearElement);
	yearElement.on('change', updateDate);
	monthElement.on('change', updateDate);
	dayElement.on('change', updateDate);
	updateDate();
    });
});
