'use strict';

const requestUrl = '/lotto/api';   //API URL

//데이터 테이블 초기화
function initDataTable() {
    //DataTable 설정
    let table = $('#table-data').DataTable({
        autoWidth: false,
        responsive: true,
        processing: true,                       //처리 중 화면 출력
        serverSide: true,                       //serverSide 설정을 통해 해당 페이지 데이터만 조회
        language: getDataTableLanguage(),       //언어 설정
        ajax: {
            type: 'GET',
            url: requestUrl,
            data: function (data) {              //조회 파라미터
                delete data.columns;
            },
            error: function (xhr, error, thrown) {
                checkRedirectLoginPage(xhr.statusText, $(location).attr('pathname'));  //로그인 페이지 리다이렉트 여부 확인

                let msg = getHttpStatusMessage(xhr.status) != '' ? getHttpStatusMessage(xhr.status) : '오류가 발생하였습니다. 잠시 후 다시 시도해 주십시오.';
                toastr.error(msg);
                $('#table-data_processing').hide();
            }
        },
        deferRender: true,
        columns: [                              //출력할 컬럼 정보
            { className: 'dt-center', data: 'num', defaultContent: '', render: $.fn.dataTable.render.text(), orderable: false },
            { className: 'dt-center', data: 'value', defaultContent: '', render: $.fn.dataTable.render.text(), orderable: false },
        ],
        dom: '<"row"<"col-sm-12"B>><"row"<"col-sm-12"tr>>',
        order: false,                           //정렬기능 비활성화
        drawCallback: function (settings, json)  //조회 완료 후 처리
        {
        },
        buttons: [
            {
                name: 'refresh',
                text: '<i class="fa fa-redo"></i> 새로고침',
                action: function () {
                    //새로고침 수행 시 데이터 조회
                    reloadTable();
                }
            }
        ]
    });
}

function reloadTable() {
    //DataTable 조회 수행
    $('#table-data').DataTable().ajax.reload();
}

$(function () {
    initDataTable();

    //마우스 우클릭 - 컨텍스트 메뉴
    $.contextMenu({
        selector: '#table-data tbody tr',
        callback: function (key, options) {
            const table = $('#table-data').DataTable();

            switch (key) {
                case 'refresh':
                    //새로고침 버튼 클릭
                    table.buttons('refresh:name').trigger();
                    break;
            }
        },

        items: {
            refresh: { name: '새로고침' },
        }
    });
});
