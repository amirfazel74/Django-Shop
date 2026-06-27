function getCsrfToken() {
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken && metaToken.content) {
        return metaToken.content;
    }

    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}

function sendArticleComment(articleId) {
    var comment = $('#commentText').val();
    var parentId = $('#parent_id').val();
    $.ajax({
        url: '/articles/add-article-comment',
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()},
        data: {
        article_comment: comment,
        article_id: articleId,
        parent_id: parentId
        }
    }).then(res => {
        $('#comments_area').html(res);
        $('#commentText').val('');
        $('#parent_id').val('');

        if (parentId !== null && parentId !== '') {
            document.getElementById('single_comment_box_' + parentId).scrollIntoView({behavior: "smooth"});
        } else {
            document.getElementById('comments_area').scrollIntoView({behavior: "smooth"});
        }
    });
}

function fillParentId(parentId) {
    $('#parent_id').val(parentId);
    document.getElementById('comment_form').scrollIntoView({behavior: "smooth"});
}

function filterProducts() {
    const filterPrice = $('#sl2').val();
    const start_price = filterPrice.split(',')[0];
    const end_price = filterPrice.split(',')[1];
    $('#start_price').val(start_price);
    $('#end_price').val(end_price);
    $('#filter_form').submit();
}

function fillPage(page) {
    $('#page').val(page);
    $('#filter_form').submit();
}

function showLargeImage(imageSrc) {
    $('#main_image').attr('src', imageSrc);
    $('#show_large_image_modal').attr('href', imageSrc);
}

function addProductToOrder(productId, count = null) {
    let productCount = count;
    if (count === null) {
        // Fallback for older inputs if quantity is not passed directly
        productCount = $('#product-count').val() || 1;
    }
    
    $.ajax({
        url: '/order/add-to-cart/',
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()},
        data: {
            product_id: productId,
            count: productCount
        }
    }).then(res => {
        Swal.fire({
            title: 'اعلان',
            text: res.text,
            icon: res.icon,
            showCancelButton: false,
            confirmButtonColor: '#047857',
            confirmButtonText: res.confirm_button_text
        }).then((result) => {
            if (result.isConfirmed && res.status === 'not_auth') {
                sessionStorage.setItem('pending_cart_product_id', productId);
                sessionStorage.setItem('pending_cart_count', productCount);
                window.location.href = '/auth/';
            } else if (res.status === 'success') {
                // Update cart count dynamically if possible
                let currentCount = parseInt($('#cart-count-badge').text()) || 0;
                // A simple page reload to update header is easiest for now
                window.location.reload();
            }
        });
    });
}

function removeOrderDetail(detailId) {
    $.ajax({
        url: '/user/remove-order-detail',
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()},
        data: {
            detail_id: detailId
        }
    }).then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body);
        }
    });
}


// detail id => order detail id
// state => increase , decrease
function changeOrderDetailCount(detailId, state) {
    $.ajax({
        url: '/user/change-order-detail',
        method: 'POST',
        headers: {'X-CSRFToken': getCsrfToken()},
        data: {
            detail_id: detailId,
            state: state
        }
    }).then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body);
        }
    });
}

$(document).ready(function() {
    if (window.isUserAuthenticated) {
        let pendingProductId = sessionStorage.getItem('pending_cart_product_id');
        let pendingCount = sessionStorage.getItem('pending_cart_count');
        if (pendingProductId) {
            sessionStorage.removeItem('pending_cart_product_id');
            sessionStorage.removeItem('pending_cart_count');
            addProductToOrder(pendingProductId, pendingCount);
        }
    }
});
