```
{
    "services": [
        {"vm_num": 2, "vm_cpu": 4}, 
        {"vm_num": 1, "vm_cpu": 4},
        {"vm_num": 3, "vm_cpu": 2}
    ],
    "cap_cpu": 8,
    "nservers": 10
}
```

Per ogni virtual machine devo decidere quale server la esegue

Vincoli:

    0) Macchina virtuale su un singolo server
    1) Le VM dello stesso servizio non possono essere eseguite nello stesso server
    2) Ogni server ha capacità limitata
    3) Vincolo su z: massimo indice di server assegnato

--- Modello 1

X[i] = v, la VM i viene eseguita dal server v

1) Se i e j sono dello stesso servizio X[i] != X[j]
2) Per ogni variabile con valore s, sommo il numero di core necessari e questo deve essere <= 8
3) Max(X[i])