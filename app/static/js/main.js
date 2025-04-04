/**
 * Ana JavaScript dosyası
 */

document.addEventListener("DOMContentLoaded", function () {
  // Tüm formları bul
  const forms = document.querySelectorAll("form");

  // Her form için gönderim olayını dinle
  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      // Form doğrulama
      if (!validateForm(form)) {
        e.preventDefault();
        return false;
      }
    });
  });

  // Form doğrulama fonksiyonu
  function validateForm(form) {
    let isValid = true;

    // Gerekli alanları kontrol et
    const requiredFields = form.querySelectorAll("[required]");
    requiredFields.forEach((field) => {
      if (!field.value.trim()) {
        isValid = false;
        showError(field, "Bu alan gereklidir.");
      } else {
        clearError(field);
      }
    });

    // Dosya yükleme alanlarını kontrol et
    const fileInputs = form.querySelectorAll('input[type="file"]');
    fileInputs.forEach((input) => {
      if (input.hasAttribute("required") && input.files.length === 0) {
        isValid = false;
        showError(input, "Lütfen bir dosya seçin.");
      } else if (input.files.length > 0) {
        // Dosya uzantısını kontrol et
        const fileName = input.files[0].name;
        const fileExt = fileName.split(".").pop().toLowerCase();

        if (input.accept) {
          const acceptedTypes = input.accept
            .split(",")
            .map((type) => type.trim().replace(".", ""));
          if (!acceptedTypes.includes(fileExt)) {
            isValid = false;
            showError(
              input,
              "Desteklenmeyen dosya formatı. Lütfen geçerli bir dosya seçin."
            );
          } else {
            clearError(input);
          }
        }
      }
    });

    return isValid;
  }

  // Hata mesajı gösterme
  function showError(field, message) {
    // Mevcut hata mesajını temizle
    clearError(field);

    // Hata mesajı oluştur
    const errorDiv = document.createElement("div");
    errorDiv.className = "invalid-feedback";
    errorDiv.textContent = message;

    // Alanın yanına hata mesajını ekle
    field.classList.add("is-invalid");
    field.parentNode.appendChild(errorDiv);
  }

  // Hata mesajını temizleme
  function clearError(field) {
    field.classList.remove("is-invalid");

    // Mevcut hata mesajını bul ve kaldır
    const parent = field.parentNode;
    const errorDiv = parent.querySelector(".invalid-feedback");
    if (errorDiv) {
      parent.removeChild(errorDiv);
    }
  }

  // Yükleme modalını kapat
  const closeModalButtons = document.querySelectorAll('[data-dismiss="modal"]');
  closeModalButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const modalId = this.dataset.target || this.getAttribute("href");
      const modal = document.querySelector(modalId);
      if (modal) {
        modal.style.display = "none";
      }
    });
  });
});
