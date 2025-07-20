document.addEventListener('DOMContentLoaded', function() {
  // Dropdown İşlevselliği
  const dropdownBtn = document.getElementById('singlePortDropdownBtn');
  const dropdown = document.getElementById('singlePortDropdown');
  const portInput = document.getElementById('singlePort');

  dropdownBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    const isVisible = dropdown.style.display === 'block';
    dropdown.style.display = isVisible ? 'none' : 'block';
    dropdownBtn.setAttribute('aria-expanded', !isVisible);
  });

  document.addEventListener('click', function() {
    dropdown.style.display = 'none';
    dropdownBtn.setAttribute('aria-expanded', 'false');
  });

  dropdown.addEventListener('click', function(e) {
    if (e.target.tagName === 'LI') {
      portInput.value = e.target.getAttribute('data-port');
      dropdown.style.display = 'none';
      dropdownBtn.setAttribute('aria-expanded', 'false');
    }
  });

  // Form Gönderimleri
  document.getElementById('singleScanForm').addEventListener('submit', handleFormSubmit);
  document.getElementById('multiScanForm').addEventListener('submit', handleFormSubmit);

  function handleFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');

    const formData = new FormData(form);
    const isMultiScan = form.id === 'multiScanForm';

    loader.style.display = 'block';
    resultDiv.style.display = 'none';

    setTimeout(function() {
      loader.style.display = 'none';
      resultDiv.style.display = 'block';

      if (isMultiScan) {
        handleMultiScanResult(formData);
      } else {
        handleSingleScanResult(formData);
      }
    }, 1500);
  }

  function handleSingleScanResult(formData) {
    const ip = formData.get('ip');
    const port = formData.get('port');

    fetch(`/api/singlescan?ip=${ip}&port=${port}`)
      .then(res => res.json())
      .then(data => {
        const status = data.status;
        const statusClass = status === 'Açık' ? 'status-open' : 'status-closed';

        document.getElementById('result').innerHTML = `PORT ${port} → <span class="${statusClass}">${status}</span>`;
        addToHistory(ip, port, status, 'Tekli');
      })
      .catch(err => {
        console.error("HATA:", err);
        document.getElementById('result').innerHTML = 'Bir hata oluştu.';
      });
  }

  function handleMultiScanResult(formData) {
    const ip = formData.get('ip');
    const start = formData.get('start');
    const end = formData.get('end');

    fetch(`/api/multiscan?ip=${ip}&start=${start}&end=${end}`)
      .then(res => res.json())
      .then(results => {
        let resultHTML = '';
        results.forEach(item => {
          const statusClass = item.status === 'Açık' ? 'status-open' : 'status-closed';
          resultHTML += `PORT ${item.port} → <span class="${statusClass}">${item.status}</span><br>`;
          addToHistory(ip, item.port, item.status, 'Çoklu');
        });

        document.getElementById('result').innerHTML = resultHTML;
      })
      .catch(err => {
        console.error("HATA:", err);
        document.getElementById('result').innerHTML = 'Bir hata oluştu.';
      });
  }

  function addToHistory(ip, port, status, scanType) {
    const historyBody = document.getElementById('historyBody');
    const statusClass = status === 'Açık' ? 'status-open' : 'status-closed';
    const now = new Date();
    const timestamp = `${now.getDate().toString().padStart(2, '0')}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getFullYear()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
      <td>${ip}</td>
      <td>${port}</td>
      <td class="${statusClass}">${status}</td>
      <td>${scanType}</td>
      <td>${timestamp}</td>
    `;

    if (historyBody.firstElementChild?.textContent.includes('Yükleniyor')) {
      historyBody.innerHTML = '';
    }

    historyBody.insertBefore(newRow, historyBody.firstChild);
    if (historyBody.children.length > 10) {
      historyBody.removeChild(historyBody.lastChild);
    }

    filterHistory(document.getElementById('dateFilter')?.value || 'all');
  }

  // 📅 Tarih Filtresi
  const filterDropdown = document.getElementById('dateFilter');
  if (filterDropdown) {
    filterDropdown.addEventListener('change', function () {
      const selected = this.value;
      filterHistory(selected);
    });
  }

  function filterHistory(range) {
    const rows = document.querySelectorAll('#historyBody tr');
    const now = new Date();
    
    // Günleri normalize etmek için yardımcı fonksiyon
    function normalizeDate(date) {
      return new Date(date.getFullYear(), date.getMonth(), date.getDate());
    }

    const todayNorm = normalizeDate(now);
    const yesterdayNorm = new Date(todayNorm);
    yesterdayNorm.setDate(yesterdayNorm.getDate() - 1);

    rows.forEach(row => {
      const dateCell = row.children[4]; // 5. sütun = tarih
      const dateText = dateCell.textContent;

      const [datePart, timePart] = dateText.split(' ');
      const [day, month, year] = datePart.split('-').map(Number);
      const [hour, minute] = timePart.split(':').map(Number);
      const rowDate = new Date(year, month - 1, day, hour, minute);
      const rowDateNorm = normalizeDate(rowDate);

      let show = true;

      if (range === 'today') {
        show = rowDateNorm.getTime() === todayNorm.getTime();
      } else if (range === 'yesterday') {
        show = rowDateNorm.getTime() === yesterdayNorm.getTime();
      } else if (range === 'last7days') {
        const diff = (todayNorm - rowDateNorm) / (1000 * 60 * 60 * 24);
        show = diff >= 0 && diff < 7;
      } else if (range === 'last30days') {
        const diff = (todayNorm - rowDateNorm) / (1000 * 60 * 60 * 24);
        show = diff >= 0 && diff < 30;
      }

      row.style.display = show ? '' : 'none';
    });
  }


  // İlk yüklemede örnek veriler
  addToHistory('192.168.1.1', 80, 'Açık', 'Tekli');
  addToHistory('192.168.1.1', 443, 'Kapalı', 'Tekli');
});
