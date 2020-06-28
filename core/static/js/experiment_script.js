// Makes list items sortable
new Sortable(sortablelist, {
    animation: 150,
    ghostClass: 'sortable-ghost'
});

// Deletes list item if botton is clicked
$("#sortablelist").on('click', '.delete', function() {   
    $(this).parent().remove();
});

// Adds a new list item to the methodology list
$(".form").on('click', '.addMethodologyBtn', function() {   
    console.log('Test')
    $("#sortablelist").append(
        ['<li class="list-group-item">',
        '<button type="button" class="delete btn-link mr-3">',
            '<img src="/static/img/trashcan-sm.svg">',
        '</button>',
        '<input  class="methodology" contenteditable="true" placeholder="Enter some text here" required>',
        '</input>',
        '</li>'].join('\n')
        );
});

// Adds indexed name attributes to list items
$( "form" ).submit(function( event ) {
    $( ".methodology" ).each(function( index ) {
        console.log(this)
        console.log(index)
        $( this ).attr('name', 'methodology_'+index);
      });
});