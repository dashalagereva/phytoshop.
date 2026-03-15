// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
    const authModal = document.getElementById("authModal");
    const openAuthBtn = document.getElementById("openAuthModalBtn");
    const authClose = document.getElementById("authModalClose");
    const loginContainer = document.getElementById("loginFormContainer");
    const registerContainer = document.getElementById("registerFormContainer");
    const showRegisterLink = document.getElementById("showRegisterForm");
    const backToLoginBtn = document.getElementById("backToLogin");

    function openModal() {
        if (!authModal) return;
        authModal.style.display = "flex";
        showLogin();
    }

    function closeModal() {
        if (!authModal) return;
        authModal.style.display = "none";
    }

    function showLogin() {
        loginContainer.style.display = "block";
        registerContainer.style.display = "none";
        document.getElementById("authModalTitle").textContent = "Вход";
    }

    function showRegister() {
        loginContainer.style.display = "none";
        registerContainer.style.display = "block";
        document.getElementById("authModalTitle").textContent = "Регистрация";
    }

    if (openAuthBtn) {
        openAuthBtn.addEventListener("click", function () {
            openModal();
        });
    }

    if (authClose) {
        authClose.addEventListener("click", function () {
            closeModal();
        });
    }

    if (showRegisterLink) {
        showRegisterLink.addEventListener("click", function (e) {
            e.preventDefault();
            showRegister();
        });
    }

    if (backToLoginBtn) {
        backToLoginBtn.addEventListener("click", function (e) {
            e.preventDefault();
            showLogin();
        });
    }

    // Закрытие по клику на фон
    if (authModal) {
        authModal.addEventListener("click", function (e) {
            if (e.target === authModal) {
                closeModal();
            }
        });
    }

    // Кнопки "Войти, чтобы купить" и т.п.
    const openLoginFromCards = document.querySelectorAll(".open-login-from-card");
    openLoginFromCards.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            openModal();
        });
    });

    const openAuthFromProduct = document.getElementById("openAuthFromProduct");
    if (openAuthFromProduct) {
        openAuthFromProduct.addEventListener("click", function (e) {
            e.preventDefault();
            openModal();
        });
    }

    const openAuthFromReview = document.getElementById("openAuthFromReview");
    if (openAuthFromReview) {
        openAuthFromReview.addEventListener("click", function (e) {
            e.preventDefault();
            openModal();
        });
    }
});
    // ===== Корзина: изменение количества и пересчёт =====
    const cartTable = document.getElementById("cartTable");
    if (cartTable) {
        const qtyInputs = cartTable.querySelectorAll(".cart-qty-input");
        const cartTotalEl = document.getElementById("cartTotal");

        qtyInputs.forEach(input => {
            input.addEventListener("change", function () {
                let qty = parseInt(this.value, 10);
                if (isNaN(qty) || qty < 1) {
                    qty = 1;
                    this.value = 1;
                }

                const row = this.closest("tr");
                const cartId = row.getAttribute("data-cart-id");
                const priceEl = row.querySelector(".cart-price");
                const rowSumEl = row.querySelector(".cart-row-sum");
                const price = parseFloat(priceEl.getAttribute("data-price"));

                // Обновляем сумму строки на клиенте
                const rowSum = price * qty;
                rowSumEl.textContent = rowSum.toFixed(2) + " ₽";

                // Отправляем запрос на сервер для сохранения
                fetch("/cart/update", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        cart_id: parseInt(cartId, 10),
                        quantity: qty
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && cartTotalEl) {
                            cartTotalEl.textContent = data.cart_total.toFixed(2);
                        }
                    })
                    .catch(err => {
                        console.error("Ошибка обновления корзины", err);
                    });
            });
        });
    }
    // ===== Админка: вкладки =====
    window.openAdminTab = function (evt, tabId) {
        const tabcontents = document.getElementsByClassName("tabcontent");
        for (let i = 0; i < tabcontents.length; i++) {
            tabcontents[i].style.display = "none";
        }

        const tablinks = document.getElementsByClassName("tablinks");
        for (let i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }

        const tab = document.getElementById(tabId);
        if (tab) tab.style.display = "block";
        if (evt && evt.currentTarget) evt.currentTarget.className += " active";
    };

    // ===== Админка: модалка продукта =====
    const productModal = document.getElementById("productModal");
    const productModalClose = document.getElementById("productModalClose");
    const productModalTitle = document.getElementById("productModalTitle");
    const openProductModalAddBtn = document.getElementById("openProductModalAdd");

    function openProductModal(mode, row) {
        if (!productModal) return;

        const idField = document.getElementById("product_id");
        const nameField = document.getElementById("product_name");
        const catField = document.getElementById("product_category_id");
        const descField = document.getElementById("product_description");
        const priceField = document.getElementById("product_price");
        const stockField = document.getElementById("product_stock");
        const activeField = document.getElementById("product_is_active");
        const existsImgField = document.getElementById("existing_image_url");
        const imgPreview = document.getElementById("product_image_preview");

        if (mode === "add") {
            productModalTitle.textContent = "Добавить продукт";
            idField.value = "";
            nameField.value = "";
            descField.value = "";
            priceField.value = "";
            stockField.value = 0;
            activeField.checked = true;
            existsImgField.value = "";
            if (imgPreview) {
                imgPreview.style.display = "none";
                imgPreview.src = "";
            }
        } else if (mode === "edit" && row) {
            productModalTitle.textContent = "Редактировать продукт";
            const pid = row.getAttribute("data-product-id");
            const pname = row.getAttribute("data-product-name");
            const pcat = row.getAttribute("data-product-category");
            const pdesc = row.getAttribute("data-product-description") || "";
            const pprice = row.getAttribute("data-product-price");
            const pstock = row.getAttribute("data-product-stock");
            const pisActive = row.getAttribute("data-product-is-active") === "1";
            const pimg = row.getAttribute("data-product-image") || "";

            idField.value = pid;
            nameField.value = pname;
            descField.value = pdesc;
            priceField.value = pprice;
            stockField.value = pstock;
            catField.value = pcat;
            activeField.checked = pisActive;
            existsImgField.value = pimg;

            if (imgPreview) {
                if (pimg) {
                    imgPreview.src = pimg;
                    imgPreview.style.display = "block";
                } else {
                    imgPreview.src = "";
                    imgPreview.style.display = "none";
                }
            }
        }

        productModal.style.display = "flex";
    }

    if (openProductModalAddBtn) {
        openProductModalAddBtn.addEventListener("click", function () {
            openProductModal("add");
        });
    }

    if (productModalClose && productModal) {
        productModalClose.addEventListener("click", function () {
            productModal.style.display = "none";
        });

        productModal.addEventListener("click", function (e) {
            if (e.target === productModal) {
                productModal.style.display = "none";
            }
        });
    }

    const productEditButtons = document.querySelectorAll(".openProductModalEdit");
    productEditButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const row = this.closest("tr");
            openProductModal("edit", row);
        });
    });
