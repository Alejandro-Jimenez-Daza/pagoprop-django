from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Modelo APARTAMENTO
class Apartamento(models.Model):
    apartamentoID = models.AutoField(primary_key=True, db_column='PK_apartamentoID')
    numeroApartamento = models.CharField(max_length=10, unique=True)
    
    class Meta:
        db_table = 'APARTAMENTO'
    
    def __str__(self):
        return f"Apartamento {self.numeroApartamento}"


# Modelo PROPIETARIO_APARTAMENTO (tabla intermedia muchos a muchos)
class PropietarioApartamento(models.Model):
    propietarioAptoID = models.AutoField(primary_key=True, db_column='PK_propietarioAptoID')
    copropietario = models.ForeignKey(
        'auth.User',  # Hace referencia a la tabla auth_user
        on_delete=models.CASCADE, 
        db_column='FK_copropietarioID',
        related_name='propietario_apartamentos'
    )
    apartamento = models.ForeignKey(
        Apartamento, 
        on_delete=models.CASCADE, 
        db_column='FK_apartamentoID',
        related_name='propietario_apartamentos'
    )
    
    class Meta:
        db_table = 'PROPIETARIO_APARTAMENTO'
        unique_together = ('copropietario', 'apartamento')
    
    def __str__(self):
        return f"{self.copropietario.username} - Apt. {self.apartamento.numeroApartamento}"


# Modelo COMPROBANTE
class Comprobante(models.Model):
    comprobanteID = models.AutoField(primary_key=True, db_column='PK_comprobanteID')
    archivo = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    copropietario = models.ForeignKey(
        'auth.User',  # Hace referencia a la tabla auth_user
        on_delete=models.CASCADE, 
        db_column='FK_copropietarioID',
        related_name='comprobantes'
    )
    apartamento = models.ForeignKey(
        Apartamento, 
        on_delete=models.CASCADE, 
        db_column='FK_apartamentoID',
        related_name='comprobantes'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'COMPROBANTE'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Comprobante ${self.monto} - {self.copropietario.username}"