function tokenLoginCheck(){

    if( window.localStorage.getItem("access_token") ){
        let headers = new Headers();
        headers.append("Authorization", window.localStorage.getItem("access_token") );
        fetch(tokenCheckUrl, {
            "method": 'GET',
            "headers": headers
        }
        ).then(
            (response) => {
                responseData = response;
                if( responseData.ok ){
                    data = responseData.json();
                    window.location.href = data.redirect_to;
                }
            })
    }
}

setTimeout(()=>{tokenLoginCheck()}, 300)
