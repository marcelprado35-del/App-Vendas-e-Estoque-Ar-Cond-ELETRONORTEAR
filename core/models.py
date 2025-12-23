from django.db import models

class Product(models.Model):
    name = models.CharField("Nome", max_length=200)
    description = models.TextField("Descrição")
    price = models.DecimalField("Preço", max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField("Quantidade em Estoque", default=0)
    image_url = models.URLField("URL da Imagem", max_length=1024, blank=True, null=True)
    commission_rate = models.DecimalField("Taxa de Comissão", max_digits=5, decimal_places=2, default=5.00)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField("Nome", max_length=200)
    email = models.EmailField("Email", max_length=254, unique=True)
    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    address = models.TextField("Endereço", blank=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.name

class Seller(models.Model):
    name = models.CharField("Nome", max_length=200)
    description = models.TextField("Descrição", blank=True, null=True)
    email = models.EmailField("Email", max_length=254, unique=True)
    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    address = models.TextField("Endereço", blank=True, null=True)
    website = models.URLField("Website", max_length=1024, blank=True, null=True)
    commission = models.DecimalField("Comissão", max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"

    def __str__(self):
        return self.name


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Cliente")
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vendedor")
    sale_date = models.DateTimeField("Data da Venda", auto_now_add=True)
    total_amount = models.DecimalField("Valor Total", max_digits=10, decimal_places=2, default=0.00)
    commission_amount = models.DecimalField("Valor da Comissão", max_digits=10, decimal_places=2, default=0.00)
    lote = models.CharField("Lote", max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

    def __str__(self):
        return f"Venda #{self.pk} - {self.customer.name}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE, verbose_name="Venda")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produto")
    lote = models.CharField("Lote", max_length=200, blank=True, null=True)
    quantity = models.PositiveIntegerField("Quantidade", default=1)
    price = models.DecimalField("Preço", max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField("Taxa de Comissão", max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"

    def __str__(self):
        return f"{self.quantity} de {self.product.name} na Venda #{self.sale.pk}"