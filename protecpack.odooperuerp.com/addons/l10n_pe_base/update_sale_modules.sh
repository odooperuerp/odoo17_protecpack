#!/bin/bash

directorio=$WORKSPACE
cd $WORKSPACE
for carpeta in "."/*/; do
    if [ -d "$carpeta" ]; then  # Verificar si es una carpeta
        # Obtener el nombre de la carpeta (sin la ruta)
        nombre_carpeta=$(basename "$carpeta")
        echo $nombre_carpeta
        # Comprimir la carpeta en un archivo zip
        zip -r "$nombre_carpeta.zip" "$nombre_carpeta"
        echo "Carpeta $nombre_carpeta comprimida."
    fi
done


carpetas="$directorio"/*.zip;
total_carpetas=$(find "$directorio" -maxdepth 1 -type f -name "*.zip" | grep -c .)
cnt=1
archivos_zip="["
for carpeta in "$directorio"/*.zip; do
    nombre_carpeta=$(basename "$carpeta")
    cnt=$((cnt + 1))
    if [ "$cnt" -gt "$total_carpetas" ]; then
        archivos_zip+="\"$nombre_carpeta\""
    else
        archivos_zip+="\"$nombre_carpeta\","
    fi
done
archivos_zip+="]"

echo "archivos zip"
echo $archivos_zip

modulos=$(curl -s --location 'https://www.codlan.com/jsonrpc'  --header 'Content-Type: application/json' --data "{\"jsonrpc\": \"2.0\",
          \"method\": \"call\",
          \"params\": {
              \"service\": \"object\",
              \"method\": \"execute\",
              \"args\": [
                  \"erp.codlan.com\", 
                  2,                                          
                  \"cae048224c260784a6db9041255695447fc38aa4\", 
                  \"product.document\",                                
                  \"search_read\",                                  
                  [[\"name\",\"in\",$archivos_zip]],
                  [\"name\"]
              ]
          }
      }")

echo $modulos

declare -a modulos_list


while IFS= read -r nombre_id; do
    modulos_list+=("$nombre_id")
done < <(echo "$modulos" | jq -r '.result[] | "\(.id) \(.name)"')

for modulo_id in $modulos_ids; do
    modulos_list+=("$modulo_id")
done

for nombre_id in "${modulos_list[@]}"; do
    read -r id nombre <<< "$nombre_id"
    archivo="$directorio/$nombre"
    
    # Verificar si el archivo existe
    if [ -f "$archivo" ]; then
        # Leer el archivo y codificarlo como base64
        base64_archivo=$(base64 "$archivo")
        base64_sin_saltos=$(echo "$base64_archivo" | tr -d '\n')
       
		response=$(echo "{\"jsonrpc\": \"2.0\",                                                                                                                                 
                    \"method\": \"call\",                                                                                                                                 
                    \"params\": {                                                                                                                                                 
                      \"service\": \"object\",                                                                                                                           
                      \"method\": \"execute\",                                                                                                                           
                      \"args\": [                                                                                                                                                     
                          \"erp.codlan.com\",                                                                                                                             
                          2,                                                                                                                                                               
                          \"cae048224c260784a6db9041255695447fc38aa4\",                                                                         
                          \"product.document\",                                                                                                                         
                          \"write\",                                                                                                                                               
                          [$id],                                                                                                                                                       
                          {\"datas\": \"$base64_sin_saltos\"}
                      ]                                                                                                                                                                         
                    }                                                                                                                                                                         
                }" | curl -H 'Connection: Keep-alive' --location 'https://www.codlan.com/jsonrpc' --header 'Content-Type: application/json' -d @- )      
        echo "El módulo $nombre con id $id ha sido actualizado" 
    else
        echo "El archivo $archivo no existe."
    fi
done