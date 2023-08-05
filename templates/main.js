 document.getElementById('myTable').addEventListener('click',function(){showElem(event)},false );
         function showElem (event) {
         console.log('Clicked row ID:', event);
      if (true) {
        let rowId = event.target.classList[0];
        console.log('Clicked row ID:', rowId);
        let url = "'/getDeliveryEntries/'".concat(rowId)
        fetch('/getDeliveryEntries/'+{{rowId}}, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(response => {})
      .catch(error => {});
    }
        document.getElementById('QtyEditPopupContainer').style.display = 'flex';
      }}