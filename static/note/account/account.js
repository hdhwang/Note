'use strict';

const requestUrl = '/account/api';   //API URL

function keyUpEvent(e)
{
    if (e.keyCode === 13)
    {
        confirmChangePassword();
    }
}

function keyDownEvent(e)
{
    if (e.keyCode === 13)
    {
        return false;
    }
}

function confirmChangePassword()
{
    let pw = document.getElementById('old_password').value;
    let newPW = document.getElementById('new_password1').value;
    let newPWConfirm = document.getElementById('new_password2').value;

    if (pw.length === 0)
    {
        showModal('경고', '기존 비밀번호를 입력하십시오.');
        return;
    }

    else if (newPW.length === 0)
    {
        showModal('경고', '신규 비밀번호를 입력하십시오.');
        return;
    }

    else if (newPW.length < 8 || newPW.length > 120)
    {
        showModal('경고', '신규 비밀번호는 8자 이상 120자 이하로 입력하십시오.');
        return;
    }

    else if (newPWConfirm.length === 0)
    {
        showModal('경고', '신규 비밀번호 확인을 입력하십시오.');
        return;
    }

    else if (newPW !== newPWConfirm)
    {
        showModal('경고', '신규 비밀번호가 일치하지 않습니다.');
        return;
    }

    showConfirmModal('확인', '비밀번호 변경 시 자동으로 로그아웃됩니다. 비밀번호를 변경하시겠습니까?',
        function (result)
        {
            if (result === true)
            {
                let param = new FormData();
                param.append('password', pw);
                param.append('new_password', newPW);

                axios(
                    {
                        method: 'PUT',
                        url: requestUrl,
                        data: param,
                    })
                    .then(function (response) {
                        if (response && response.status == 200) {
                            window.location.herf = '/';
                        }
                        else {
                            let msg = '비밀번호 변경에 실패하였습니다. ' + getHttpStatusMessage(response.status);
                            toastr.error(msg);
                        }
                    })
                    .catch(function (error) {
                        checkRedirectLoginPage(error, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인
                        let msg = '비밀번호 변경에 실패하였습니다. ';
                        if (error.response.status == 404) {
                            msg += '기존 비밀번호가 일치하지 않습니다.';
                        }
                        else {
                            msg += getHttpStatusMessage(error.response.status);
                        }
                        toastr.error(msg);
                    });
            }
        }
    );
}

$(function () { 
});