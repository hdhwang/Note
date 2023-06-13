'use strict';

const errMsg = '조회 오류';
const baseUrl = '/dashboard/api/';

// 중지를 위해 타이머 ID 보관
let bankAccountTimerId = null;
let serialTimerId = null;
let noteTimerId = null;
let guestBookTimerId = null;

const interval = 5000;

function getBankAccountCount() {
    axios.get(baseUrl + 'bank-account').then(function (response) {
        checkRedirectLoginPage(response, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인

        if (response.data && response.data.count >= 0) {
            const count = response.data.count;
            $('#bank-account').html(numberWithComma(count));

            $('#bank-account-overlay').hide();
        }
    }).catch(function (error) {
        $('#bank-account').html(errMsg);
        $('#bank-account-overlay').hide();
    });
}

function getSerialCount() {
    axios.get(baseUrl + 'serial').then(function (response) {
        checkRedirectLoginPage(response, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인

        if (response.data && response.data.count >= 0) {
            const count = response.data.count;
            $('#serial').html(numberWithComma(count));
            $('#serial-overlay').hide();
        }
    }).catch(function (error) {
        $('#serial').html(errMsg);
        $('#serial-overlay').hide();
    });
}

function getNoteCount() {
    axios.get(baseUrl + 'note').then(function (response) {
        checkRedirectLoginPage(response, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인

        if (response.data && response.data.count >= 0) {
            const count = response.data.count;
            $('#note').html(numberWithComma(count));
            $('#note-overlay').hide();
        }
    }).catch(function (error) {
        $('#note').html(errMsg);
        $('#note-overlay').hide();
    });
}

function getGuestBookCount() {
    axios.get(baseUrl + 'guest-book').then(function (response) {
        checkRedirectLoginPage(response, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인

        if (response.data && response.data.count >= 0) {
            const count = response.data.count;
            $('#guest-book').html(numberWithComma(count));
            $('#guest-book-overlay').hide();
        }
    }).catch(function (error) {
        $('#guest-book').html(errMsg);
        $('#guest-book-overlay').hide();
    });
}

// 타이머 중단
function stopTimer(id) {
    if (id != null) {
        clearInterval(id);
    }
}

function checkEmptyData(itemList) {
    for (let i = 0; i < itemList.length; i++) {
        if (itemList[i].length > 0) {
            return false;
        }
    }

    return true;
}

function setEmptyData() {
    $('#dashboard').append('<div class="col-lg-12 text-muted"><h4>대시보드에 출력할 데이터가 없습니다.</h4></div>');
}

$(function () {
    const itemList = [$('#bank-account'), $('#serial'), $('#note'), $('#guest-book')];

    //출력할 대시보드 데이터가 없는 경우
    if (checkEmptyData(itemList)) {
        setEmptyData();
    }

    //출력할 대시보드 데이터가 존재하는 경우
    else {
        // 계좌번호 수 조회
        if ($('#bank-account').length > 0) {
            getBankAccountCount();
            bankAccountTimerId = setInterval(function () {
                getBankAccountCount();
            }, interval);
        }

        // 시리얼 번호 개수 조회
        if ($('#serial').length > 0) {
            getSerialCount();
            serialTimerId = setInterval(function () {
                getSerialCount();
            }, interval);
        }

        // 노트 개수 조회
        if ($('#note').length > 0) {
            getNoteCount();
            noteTimerId = setInterval(function () {
                getNoteCount();
            }, interval);
        }

        // 결혼식 방명록 개수 조회
        if ($('#guest-book').length > 0) {
            getGuestBookCount();
            guestBookTimerId = setInterval(function () {
                getGuestBookCount();
            }, interval);
        }
    }
});