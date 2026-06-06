# Proyecto Final — Bases de Datos: Sistema de Información.
El sistema está diseñado para la Cooperativa de Ahorro y Crédito COOVALLUNA Ltda.

## Integrantes del equipo

| Nombre Completo                  | Código  | Rol         | Correo Electrónico                                                                 |
|----------------------------------|---------|-------------|------------------------------------------------------------------------------------|
| Santiago Serrano Morales         | 2477006 | Colaborador | [serrano.santiago@correounivalle.edu.co](mailto:serrano.santiago@correounivalle.edu.co) |
| Samuel Esteban Peña Jaramillo    | 2477399 | Colaborador | [samuel.pena@correounivalle.edu.co](mailto:samuel.pena@correounivalle.edu.co)           |
| Dayan Stefany Marulanda Pulido   | 2477427 | Colaborador | [dayan.marulanda@correounivalle.edu.co](mailto:dayan.marulanda@correounivalle.edu.co)   |
| Laura Sofía Echeverry González   | 2477067 | Colaborador | [echeverry.laura@correounivalle.edu.co](mailto:echeverry.laura@correounivalle.edu.co)   |

---

## Estado del proyecto

### Primera Entrega — 10 de mayo de 2026 (4.8) ✅

| Componente | Peso | Estado |
|---|---|---|
| Historias de usuario (20 historias, 3 perfiles) | 25% | ✅ Entregado |
| Modelo Entidad-Relación en notación Chen | 65% | ✅ Entregado |
| Mockups de baja fidelidad | 15% | ✅ Entregado |

### Segunda Entrega — 25 de mayo de 2026 (5.0) ✅

| Componente | Peso | Estado |
|---|---|---|
| Correcciones de la primera entrega con nota de cambios | 10% | ✅ Entregado |
| Transformación MER → esquema relacional | 30% | ✅ Entregado |
| Verificación de normalización hasta 3FN | 30% | ✅ Entregado |
| Script DDL funcional y completo | 30% | ✅ Entregado |

### Entrega Final — 9 de junio de 2026 ⏳

| Componente | Peso | Estado |
|---|---|---|
| Documento PDF integrado | 10% | ⏳ Pendiente |
| Producto de software funcionando | 50% | ⏳ Pendiente |
| Presentación, sustentación y video | 40% | ⏳ Pendiente |

---

## Estructura del repositorio
```texto
app/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── asesor.py
│   │   ├── asociado.py
│   │   └── reportes.py
│   └── utils/
│       └── helpers.py
│
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard_admin.html
│   │   ├── dashboard_asesor.html
│   │   ├── dashboard_asociado.html
│   │   ├── agencias.html
│   │   ├── empleados.html
│   │   ├── asociados.html
│   │   ├── beneficiarios.html
│   │   ├── cuentas.html
│   │   ├── movimientos.html
│   │   ├── creditos.html
│   │   ├── pagos.html
│   │   ├── reportes.html
│   │   └── error.html
│   │
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   └── main.js
│       └── img/
│
├── requirements.txt
├── .env
└── .gitignore
```


---

## Opciones tecnológicas declaradas

- **RDBMS:** PostgreSQL 15 o superior
- **Control de versiones:** Git + GitHub
