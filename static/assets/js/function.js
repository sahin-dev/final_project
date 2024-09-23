console.log("working fine");

const monthNames = months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];



$("#commentForm").submit(function(e) {

    e.preventDefault();

    let dt = new Date();
    let time = dt.getDate() + " " + monthNames[dt.getUTCMonth()] + ", " + dt.getFullYear()+ " ";

//review

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function(response) {
            console.log("Comment saved to DB");


            if(response.bool == true){
                $("#review-rsp").html("Review Added Successfully.!!")
                $(".hide-comment-form").hide()
                $(".add-review").hide()


                
                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                    _html += '<div class="user justify-content-between d-flex">'
                    _html += '<div class="thumb text-center">'
                    _html += ' <img src="https://img.freepik.com/free-vector/illustration-businessman_53876-5856.jpg" alt="" />'
                    _html += '<a href="#" class="font-heading text-brand">'+ response.context.user +'</a>'
                    _html += '</div>'

                    _html += ' <div class="desc">'
                    _html += ' <div class="d-flex justify-content-between mb-10">'
                    _html += ' <div class="d-flex align-items-center">'
                    _html += ' <span class="font-xs text-muted">'+ time +' </span>'
                    _html += ' </div>'

                    for(let i = 1; i <= response.context.rating; i++){
                        _html += '<i class="fas fa-star text-warning"></i>'
                    }

                    _html += '</div>'
                    _html += ' <p class="mb-10"> '+ response.context.review +' </p>'

                    _html += ' </div>'
                    _html += ' </div>'
                    _html += '</div>'
                    $(".comment-list").prepend(_html)
            }

            $(".comment-list").prepend(_html)
            // console.log(response);
        },
        // error: function(xhr, status, error) {
        //     console.error("An error occurred: " + status + " - " + error);
        // }
    });
});
//filter

$(document).ready(function (){
    $(".filter-checkbox, #price-filter-btn").on("click", function(){
        console.log("   A check");

        let filter_object = {}

        let min_price = $("#max_price").attr("min")
        let max_price = $("#max_price").val()

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val()
            let filter_key =$(this).data("filter")


            // console.log("filter value:",filter_value);
            // console.log("filter key:",filter_key);

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter = ' + filter_key  + ']:checked')).map(function(element){
                return element.value
            })
        })
        console.log("Filter object is:", filter_object)
        $.ajax({
            url : '/filter-product',
            data: filter_object,
            dataType : 'json',
            beforeSend: function(){
                console.log('sending data');
            },
            success: function(response){
                console.log(response)
                $("#filtered-product").html(response.data)
            }

        })
    })

    // price filtering
    $("#max_price").on("blur", function(){
        let min_price = $(this).attr("min")
        let max_price = $(this).attr("max")
        let current_price = $(this).val()
        
        // console.log("current price is:", min_price);

        if(current_price < parseInt(min_price) || current_price > parseInt(max_price)){
           console.log("Eroor");
           min_price = Math.round(min_price * 100) / 100
           max_price = Math.round(max_price * 100) / 100
        //    console.log("min", min_Price)
        alert("Price must be between ৳" +min_price+ " and ৳" + max_price)
        $(this).val(min_price)
        
        $('#range').val(min_price)
        $(this).focus()

        return false



        }
    })
    //Add to card Funtionality

    $(".add-to-cart-btn").on("click", function() {

        let this_val = $(this);
        let index = this_val.attr("data-index");




        let quantity = $(".product-quantity-" + index).val();
        let product_title = $(".product-title-" + index).val();

        let product_id = $(".product-id-" + index).val();
        let product_price = $(".current-product-price-" + index).text();

        let product_pid = $(".product-pid-" + index).val();
        let product_image = $(".product-image-" + index).val();
        

        console.log(quantity, product_id, product_title, product_price, this_val,product_pid,product_image);

        $.ajax({
            url: '/add-to-cart',
            data: {
                'id' : product_id,
                'pid' : product_pid,
                'image' : product_image,
                'qty' : quantity,
                'title' : product_title,
                'price' : product_price,

            },
            dataType: 'json',
            beforeSend: function(){
                console.log("addi cart///");

            },
            success: function(response){
                // this_val.html("✔")
                // this_val.html('<span class="checkmark">&#10004;</span>');
                this_val.html('<i class="fas fa-check custom-check"></i>');
                console.log("added!")
                $(".cart-items-count").text(response.totalcartitems)


            }

        })
    });

    // $(".delete-product").on("click", function() {
    $(document).on("click", '.delete-product', function(){
        let product_id = $(this).attr("data-product")
        let this_val = $(this)
        console.log(product_id);

        $.ajax({
            url: "/delete-from-cart",
            data: {
                "id": product_id
            },
            dataType: "json",
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems)
                $("#cart-list").html(response.data)


            }

        })

    })

    $(".update-product").on("click", function(){

        let product_id = $(this).attr("data-product")
        let this_val = $(this)
        let product_quantity = $(".product-qty-"+product_id).val()
        console.log(product_id);
        console.log(product_quantity);

        $.ajax({
            url: "/update-cart",
            data: {
                "id": product_id,
                "qty": product_quantity,
            },
            dataType: "json",
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems)
                $("#cart-list").html(response.data)


            }

        })

    })

    //adding to wishlist
    $(document).on("click", ".add-to-wishlist", function(){
        let product_id = $(this).attr("data-product-item")
        let this_val = $(this)
        $.ajax({
            url: "/add-to-wishlist",
            data: {
                "id": product_id
            },
            dataType: "json",
            beforeSend: function(){
                // this_val.html('<i class="fas fa-check custom-check"></i>');
                console.log("adding...");
            },
            success:function(response){
                this_val.html('<i class="fas fa-check custom-check"></i>');
                if (response.bool === true) {
                    console.log("wish");
                    // $(".pro-count").text(response.wishlist_count);

                }
                

            }
        })

    })
       


    //remove from wishlist
    $(document).on("click", ".delete-wishlist-product", function(){
        
        let wishlist_id = $(this).attr("data-wishlist-product");  // Updated to match the HTML attribute
        let this_val = $(this);



        

        console.log("wishlist id is:", wishlist_id);

        $.ajax({
            url:"/remove-from-wishlist",
            data: {
                "id" : wishlist_id
            },
            dataType: "json",
            beforeSend:function(){
                console.log("deleting product");
            },
            success: function(response) {
                console.log("AJAX Response:", response);
                $("#wishlist-list").html(response.data);
                // $(".pro-count").text(response.wishlist_count);
            }
        })
    })


    


})












// $(".add-to-cart-btn").on("click", function() {
//     let quantity = $("#product-quantity").val();
//     let product_title = $(".product-title").val();
//     let product_id = $(".product-id").val();
//     let product_price = $("#current-product-price").text();
//     let this_val = $(this);

//     console.log(quantity, product_id, product_title, product_price, this_val);

//     $.ajax({
//         url: '/add-to-cart',
//         data: {
//             'id' : product_id,
//             'qty' : quantity,
//             'title' : product_title,
//             'price' : product_price,

//         },
//         dataType: 'json',
//         beforeSend: function(){
//             console.log("addi cart///");

//         },
//         success: function(response){
//             this_val.html("Item Added to Cart")
//             console.log("added!")
//             $(".cart-items-count").text(response.totalcartitems)


//         }

//     })
// });
