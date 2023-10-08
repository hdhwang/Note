function confirmLogout() {
    showConfirmModal('확인', '로그아웃하시겠습니까?',
        function (result) {
            if (result === true) {
                location.href = '/logout';
            }
        }
    );
}

function showModal(title, message, callbackFunc = null) {
    if (title.length > 0 && message.length > 0) {
        let modal = '<div class="modal fade" id="notify-modal"><div class="modal-dialog"><div class="modal-content">' +
            '<div class="modal-header"><h4 class="modal-title" id="confirm-modal-title"></h4>' +
            '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>' +
            '<div class="modal-body" id="confirm-modal-body"><p></p></div>' +
            '<div class="modal-footer">' +
            '<button type="button" class="btn btn-primary" id="btn-ok" data-dismiss="modal">확인</button>' +
            '</div></div></div></div>';

        $('#main-contents').append(modal);

        $('#confirm-modal-title').text(title);  //타이틀 지정
        $('#confirm-modal-body').html(message); //메시지 지정

        //모달이 출력될 때 확인 버튼에 포커스
        $('#notify-modal').off('shown.bs.modal').on('shown.bs.modal', function () {
            $('#btn-ok').focus();
        });

        //모달이 닫힐 때 모달 폐기
        $('#notify-modal').off('hidden.bs.modal').on('hidden.bs.modal', function () {
            $('#notify-modal').remove();
        });

        //확인 버튼 클릭 시 true 리턴
        $('#notify-modal').off('click').on('click', '#btn-ok', function () {
            if (callbackFunc) {
                callbackFunc();
            }

            $('#notify-modal').remove();
        });

        $('#notify-modal').attr('tabindex', -1);
        $('#notify-modal').modal({
            show: true,
            backdrop: 'static',
            keyboard: true
        });
    }
}

function showConfirmModal(title, message, callbackFunc) {
    if (title.length > 0 && message.length > 0) {
        let modal = '<div class="modal fade" id="confirm-modal"><div class="modal-dialog"><div class="modal-content"><div class="modal-header">' +
            '<h4 class="modal-title" id="confirm-modal-title""></h4>' +
            '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>' +
            '<div class="modal-body" id="confirm-modal-body"><p></p></div>' +
            '<div class="modal-footer">' +
            '<button type="button" class="btn btn-primary" id="btn-confirm-ok" data-dismiss="modal">확인</button>' +
            '<button type="button" class="btn btn-default pull-right" id="btn-confirm-cancel" data-dismiss="modal">취소</button>' +
            '</div></div></div></div>';

        $('#main-contents').append(modal);

        $('#confirm-modal-title').text(title);  //타이틀 지정
        $('#confirm-modal-body').html(message); //메시지 지정

        //확인 버튼에 포커스
        $('#confirm-modal').off('shown.bs.modal').on('shown.bs.modal', function () {
            $('#btn-confirm-ok').focus();
        });

        //모달이 닫힐 때 모달 폐기
        $('#confirm-modal').off('hidden.bs.modal').on('hidden.bs.modal', function () {
            $('#confirm-modal').remove();
        });

        //확인 버튼 클릭 시 true 리턴
        $('#confirm-modal').off('click').on('click', '#btn-confirm-ok', function () {
            callbackFunc(true);
            $('#confirm-modal').remove();
        });

        $('#confirm-modal').attr('tabindex', -1);
        $('#confirm-modal').modal({
            show: true,
            backdrop: 'static',
            keyboard: true
        });
    }
}

// 비밀번호 입력 모달 출력
function showPasswordModal(message, callbackFunc) {
    message = (message !== null && message !== undefined || message !== '') ? message : '비밀번호를 입력해 주십시오.';
    let emptyMessage = '비밀번호를 입력해 주십시오.';

    let modal = '<div class="modal fade" id="modal-pw"><div class="modal-dialog vertical-align-center"><div class="modal-content"><div class="modal-header">' +
        '<h4 class="modal-title">비밀번호 확인</h4>' +
        '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>' +
        '<div class="modal-body">' +
        '<h1 align="center"><i class="fa fa-warning"></i></h1>' +
        '<h6 align="center" id="pw-modal-message"></h6>' +
        '<input type="password" id="input-pw" class="form-control" minlength="8" maxlength="120"/>' +
        '</div>' +
        '<div class="modal-footer">' +
        '<button type="button" class="btn btn-primary" id="btn-pw-ok" data-dismiss="modal">확인</button>' +
        '<button type="button" class="btn btn-default pull-right" id="btn-pw-cancel" data-dismiss="modal">취소</button>' +
        '</div></div></div></div>';

    $('#main-contents').append(modal);
    $('#pw-modal-message').text(message); //메시지 지정

    //비밀번호 입력 input에 포커스
    $('#modal-pw').off('shown.bs.modal').on('shown.bs.modal', function () {
        $('#input-pw').focus();
    });

    //모달이 닫힐 때 모달 폐기
    $('#modal-pw').off('hidden.bs.modal').on('hidden.bs.modal', function () {
        $('#modal-pw').remove();
    });

    //패스워드 입력 input에서 엔터 키 입력 시
    $('#input-pw').keypress(function (e) {
        if (!$('#btn-pw-ok').attr('disabled') && e.which == 13) {
            changePWModalBtnStatus(false);      //확인 버튼 비활성화

            //여러 번 클릭하여 요청하는 것을 방지하기 위해 0.5초 딜레이를 줌
            setTimeout(function () {
                if ($('#input-pw').val() === '') {
                    showModal('경고', emptyMessage);
                    changePWModalBtnStatus(true);   //확인 버튼 활성화
                }

                else {
                    callbackFunc($('#input-pw').val());
                }
            }, 500);
        }
    });

    //확인 버튼 클릭 시 true 리턴
    $('#modal-pw').off('click', '#btn-pw-ok').on('click', '#btn-pw-ok', function () {
        changePWModalBtnStatus(false);      //확인 버튼 비활성화
        const val = $('#input-pw').val();

        //여러 번 클릭하여 요청하는 것을 방지하기 위해 0.5초 딜레이를 줌
        setTimeout(function () {
            if (val == '') {
                showModal('경고', emptyMessage);
                changePWModalBtnStatus(true);   //확인 버튼 활성화
            }

            else {
                callbackFunc(val);
            }
        }, 500);
    });

    $('#modal-pw').attr('tabindex', -1);
    $('#modal-pw').modal({
        show: true,
        backdrop: 'static',
        keyboard: true
    });
}

// 비밀번호 입력 모달 > 확인 버튼 활성화 / 비활성화
function changePWModalBtnStatus(enabled) {
    enabled = (enabled == false) ? true : false;
    $('#btn-pw-ok').attr('disabled', enabled);
}

// 비밀번호 입력 모달 닫기
function closePasswordModal() {
    if ($('#modal-pw').length > 0) {
        $('#modal-pw').modal('hide');
    }
}

//Form 데이터 전체 초기화
function clearFormData(target) {
    if (target !== null) {
        if ($(target).find('form') && $(target).find('form').length > 0) {
            $(target).find('form')[0].reset();
        }

        $(target).find('input').each(function () {
            if ($(this).attr('type') == 'checkbox') {
                $(this).prop('checked', false);
            }

            else {
                $(this).val();
            }
        });

        $(target).find('select').each(function () {
            $(this).children('option:eq(0)').prop('selected', true);
        });
    }

    initICheck();
}

//최대 길이 체크
function maxLengthCheck(object) {
    if (object.value.length > object.maxLength) {
        object.value = object.value.slice(0, object.maxLength);
    }
}

function getCookiePath() {
    return ';path=note';
}

//쿠키 설정
function setCookie(cookieName, value, exDays, setPath = false) {
    let expireDate = new Date();
    expireDate.setDate(expireDate.getDate() + exDays);
    let cookieValue = escape(value) + ((exDays == null) ? "" : "; expires=" + expireDate.toGMTString());

    let cookie = cookieName + '=' + cookieValue;
    if (setPath == true) {
        cookie += getCookiePath();
    }
    document.cookie = cookie;
}

//쿠키 삭제
function deleteCookie(cookieName, setPath = false) {
    let expireDate = new Date();
    expireDate.setDate(expireDate.getDate() - 1);

    let delCookie = cookieName + '= ; expires=' + expireDate.toGMTString();
    if (setPath == true) {
        delCookie += getCookiePath();
    }
    document.cookie = delCookie;
}

//쿠키 조회
function getCookie(cookieName) {
    cookieName = cookieName + '=';
    let cookieData = document.cookie;
    let start = cookieData.indexOf(cookieName);
    let cookieValue = '';
    if (start != -1) {
        start += cookieName.length;
        let end = cookieData.indexOf(';', start);
        if (end == -1) {
            end = cookieData.length;
        }

        cookieValue = cookieData.substring(start, end);
    }
    return unescape(cookieValue);
}

//이메일 유효성 검증
function checkEmailValidation(inputText) {
    const emailRegex = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;//이메일 정규식

    let emailList = inputText.split(';');
    for (let i in emailList) {
        if (!emailRegex.test(emailList[i])) {
            return false;
        }
    }

    return true;
}

//콤마찍기
function numberWithComma(num) {
    num = String(num);
    return num.replace(/(\d)(?=(?:\d{3})+(?!\d))/g, '$1,');
}

//DateRangePicker 언어 설정 조회
function getDateRangePickerLocale(format = 'YYYY-MM-DD HH:mm') {
    return {
        format: format,
        separator: ' ~ ',
        customRangeLabel: '기간 설정',
        applyLabel: '적용',
        cancelLabel: '취소',
        monthNames: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
        daysOfWeek: ['일', '월', '화', '수', '목', '금', '토'],
    }
}

//DataTable 언어 설정 조회
function getDataTableLanguage(param = '') {
    let url = '/data-tables/korean';
    if (param != '') {
        url += param
    }

    return {
        url: url
    };
}

//iCheck 초기화
function initICheck() {
    //iCheck for checkbox and radio inputs
    $('input[type="checkbox"].square, input[type="radio"].square').iCheck({
        checkboxClass: 'icheckbox_square-blue',
        radioClass: 'iradio_square-blue'
    });

    $('input[type="checkbox"].minimal, input[type="radio"].minimal').iCheck({
        checkboxClass: 'icheckbox_minimal-blue',
        radioClass: 'iradio_minimal-blue'
    });

    $('input[type="checkbox"].flat, input[type="radio"].flat').iCheck({
        checkboxClass: 'icheckbox_flat-blue',
        radioClass: 'iradio_flat-blue'
    });

    //Flat green color scheme for iCheck
    $('input[type="checkbox"].flat-green, input[type="radio"].flat-green').iCheck({
        checkboxClass: 'icheckbox_flat-green',
        radioClass: 'iradio_flat-green'
    });
}

//검색 기간(초) 조회
function getDiffDateRange(dateRangePicker) {
    let startDate = dateRangePicker.data('daterangepicker').startDate;
    let endDate = dateRangePicker.data('daterangepicker').endDate;

    return (endDate - startDate) / 1000;
}

// 로그인 페이지 리다이렉트 체크
function checkRedirectLoginPage(data, next = '') {
    let url = '/';
    if (next != '') {
        url += '?next=' + next;
    }

    if (data == 'parsererror') {
        location.replace(url);
    }
    else if (data && data.request && data.request.responseURL && data.request.responseURL.indexOf('?next=') > -1) {
        location.replace(url);
    }
    else if (data.toString().indexOf('Unauthorized') > -1) {
        location.replace(url);
    }
    else if (data.toString().indexOf('Error: Request failed with status code 401') > -1) {
        location.replace(url);
    }
    else if (data.toString().indexOf('Error: Request failed with status code 405') > -1) {
        location.replace(url);
    }
    else if (data.toString().indexOf('Error: Request failed with status code 500') > -1) {
        location.replace(url);
    }
}

// HTTP 상태 코드별 메시지 조회
function getHttpStatusMessage(status, item = '항목') {
    let msg = '';

    if (status == 401) {
        msg = '요청에 대한 권한이 없습니다.';
    }

    else if (status == 403) {
        msg = '요청에 대한 권한이 없습니다.';
    }

    else if (status == 404) {
        msg = '요청 페이지를 찾을 수 없습니다.';
    }

    else if (status == 405) {
        msg = '허용되지 않는 요청 방식입니다.';
    }

    else if (status == 409) {
        msg = '이미 존재하는 {0}입니다.'.replace('{0}', item);
    }

    else if (status == 500) {
        msg = '서버에 오류가 발생하였습니다.';
    }

    return msg;
}

//XSS 관련 html 코드 치환
function escapeHtml(text) {
    if (text != null && text != undefined && typeof (text) == typeof '') {
        text = text.replace(/\</g, "&lt;");
        text = text.replace(/\>/g, "&gt;");
        text = text.replace(/\(/g, "&lpar;");
        text = text.replace(/\)/g, "&lrar;");
        text = text.replace(/\#/g, "&num;");
        text = text.replace(/\&/g, "&amp;");
        text = text.replace(/\'/g, "&aposl;");
        text = text.replace(/\"/g, "&quot;");
    }

    return text
}

function getDataTablesDom() {
    let dom = '<"row"<"col-sm-4"l><"col-sm-8"B>>'
        + '<"row"<"col-sm-4"i><"col-sm-8"p>>'
        + '<"row"<"col-sm-12"tr>>';

    return dom;
}

function getDataTablesOrder(data) {
    let column = data.order[0].column;
    let dir = (data.order[0].dir == 'desc') ? '-' : '';
    let order = (data.columns[column].data) ? data.columns[column].data : 'id';

    return { 'order': order, 'dir': dir };
}

function getDataTablesFilterColumns(data) {
    let result = [];

    for (let i = 0; i < data.columns.length; i++) {
        if (data.columns[i].search.value) {
            result.push({ 'data': data.columns[i].data, 'value': data.columns[i].search.value })
        }
    }

    return result;
}

function checkJSONFormat(data) {
    if (typeof (data) == 'object') {
        try {
            data = JSON.stringify(data);
        }

        catch (e) {
            return false;
        }
    }

    if (typeof (data) == 'string') {
        try {
            data = JSON.parse(data);
        }

        catch (e) {
            return false;
        }
    }

    if (typeof (data) != 'object') {
        return false;
    }

    return true;
}

// 로컬 스토리지 데이터 조회
function getLocalStorageData(key) {
    let localStorageData = localStorage.getItem(key);

    return checkJSONFormat(localStorageData) ? JSON.parse(localStorageData) : localStorageData;
}

// 로컬 스토리지 데이터 설정
function setLocalStorageData(key, value) {
    if (key) {
        localStorage.setItem(key, (checkJSONFormat(value) == true) ? JSON.stringify(value) : value);

        return true;
    }

    return false;
}

// 로컬 스토리지 데이터 삭제
function removeLocalStorageData(key) {
    if (key && localStorage.getItem(key)) {
        localStorage.removeItem(key);

        return true;
    }

    return false;
}

// 토큰 만료 점검 및 새로고침 수행
function checkToken() {
    const url = '/';
    const access_exp = getCookie('access_exp');
    const refresh_exp = getCookie('refresh_exp');

    // 현재 페이지가 메인 페이지인 경우
    if (window.location.pathname == url) {
        return;
    }
    // 토큰이 존재하지 않거나 refresh_token이 만료된 경우 메인 페이지로 이동
    else if (checkTokenExpiration(refresh_exp)) {
        window.location.href = url;
    }
    // access_token이 만료 또는 만료 예정인 경우 토큰 새로고침 수행
    else if (checkTokenExpiration(access_exp)) {
        refreshToken();
    }
}

// 토큰 새로고침 수행
function refreshToken() {
    const requestUrl = '/note/refresh-token';   //API URL
    axios(
        {
            method: 'POST',
            url: requestUrl,
        })
        .catch(function (error) {
            checkRedirectLoginPage(error, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인
            // console.log(error);
        });
}

// 토큰 만료 점검
function checkTokenExpiration(exp) {
    const expiredTime = new Date(exp).getTime();
    const nowTime = new Date(Date.now()).getTime();
    if (nowTime + 30 < expiredTime) {
        return false;
    }
    return true;
}

$(function () {
    // CSRF 토큰을 쿠키가 아닌 base.html의 djagno 변수에서 조회
    const csrfToken = $('[name=csrfmiddlewaretoken]').val();
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

    //Modal에 Drag & Drop 기능 추가
    $('.modal-dialog').draggable({ handle: ".modal-header" });

    // 매 초마다 토큰 만료 점검 수행
    setInterval(function () {
        checkToken();
    }, 1000);
});