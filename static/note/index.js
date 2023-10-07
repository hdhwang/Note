function loginClickEvent() {
    if ($.trim($('#user-id').val()) == '') {
        showModal('경고', '아이디를 입력해 주십시오.');
    }

    else if ($.trim($('#user-password').val()) == '') {
        showModal('경고', '비밀번호를 입력해 주십시오.');
    }

    else {
        let param = new FormData();
        param.append('username', $('#user-id').val());
        param.append('password', $('#user-password').val());

        tryLogin(param);
    }
}

function tryLogin(param) {
    const errMsg = '아이디 또는 비밀번호가 일치하지 않습니다.';
    axios(
        {
            method: 'POST',
            url: '/note/login',
            data: param,
        })
        .then(function (response) {
            if (response && response.status == 200) {
                // 토큰을 쿠키에 저장
                setCookie('access', response.data.access);
                setCookie('refresh', response.data.refresh);

                window.location = window.location.origin + $('#next').val();
            }

            else {
                showModal('알림', errMsg);
            }
        })
        .catch(function (error) {
            showModal('알림', errMsg);
            // console.log(error);
        });
}

$(function () {
    // CSRF 토큰을 쿠키가 아닌 base.html의 djagno 변수에서 조회
    const csrfToken = $('[name=csrfmiddlewaretoken]').val();
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

    // 저장된 쿠키값을 가져와서 아이디 칸에 넣어준다. 없으면 공백으로 들어감.
    let key = getCookie('key');
    let expiredDate = 7;

    $('#user-id').val(key);

    // 그 전에 아이디를 저장해서 처음 페이지 로딩 시, 입력 칸에 저장된 아이디가 표시된 상태라면,
    if ($("#user-id").val() != '') {
        $('#id-save-check').iCheck('check');    // 아이디 저장 체크 상태로 두기

        //출력된 모달이 없는 경우 비밀번호에 포커스
        if ($('#modal').length == 0) {
            $('#user-password').focus();
        }
    }
    else {
        //출력된 모달이 없는 경우 아이디에 포커스
        if ($('#modal').length == 0) {
            $('#user-id').focus();
        }
    }

    $('#id-save-check').off('ifChanged').on('ifChanged', function (event)     // 체크박스에 변화가 있다면,
    {
        if (event.target.checked)                           // 아이디 저장 체크했을 때,
        {
            setCookie('key', $('#user-id').val(), expiredDate); // 7일 동안 쿠키 보관
        }

        else                                                // 아이디 저장 체크 해제 시,
        {
            deleteCookie('key');
        }
    });

    // 아이디 저장을 체크한 상태에서 아이디를 입력하는 경우에도 쿠키 저장.
    $('#user-id').keyup(function ()                 // 아이디 입력 칸에 아이디를 입력할 때,
    {
        if ($('#id-save-check').is(':checked'))     // 아이디 저장 체크했을 때,
        {
            setCookie('key', $('#user-id').val(), expiredDate); // 7일 동안 쿠키 보관
        }
    });

    //아이디 입력 창에 엔터 클릭 이벤트 추가
    $('#user-id, #user-password').off('keypress').on('keypress', function () {
        const char = event.keyCode;

        if (char == 13) {
            loginClickEvent();
        }
    });

    //로그인 버튼에 클릭 이벤트 추가
    $('#login-btn').off('click').on('click', function () {
        loginClickEvent();
    });
});