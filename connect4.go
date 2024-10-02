package main

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"net"
	"os"
	"strconv"
)

var coins int = 18
var random_port = "8001"
var main_port = "8001"

func main() {
	GenerateListenConnectionToStart()
	GenerateListenConnectionToPlay()
}

func GenerateMove() int {
	coins -= 1
	column := ChooseColumnRandom()
	print("\nColumna: ", column+1)
	print("\nFicha:  ", coins)
	return column
}

func ChooseColumnRandom() int {
	randomNumber, _ := rand.Int(rand.Reader, big.NewInt(6))
	return int(randomNumber.Int64())
}

func GeneratePort() int {
	randomNumber, _ := rand.Int(rand.Reader, big.NewInt(65535-8000+1))
	randomNumber.Add(randomNumber, big.NewInt(8000))
	return int(randomNumber.Int64())
}

func GenerateListenConnectionToStart() {

	address := "127.0.0.1:" + main_port
	udpAddr, _ := net.ResolveUDPAddr("udp", address)

	middleware, err := net.ListenUDP("udp", udpAddr)
	print("\naddress: ", address)
	print("\nupdAddr: ", udpAddr.IP.String(), "	Port: ", strconv.Itoa(udpAddr.Port))
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	buffer := make([]byte, 1024)
	n, addr, err := middleware.ReadFromUDP(buffer)
	print("\nMensaje: ")
	data := buffer[:n]
	if err != nil {
		fmt.Println(err)
		return
	}

	print("\n", string(data))
	random_port = strconv.Itoa(GeneratePort())
	middleware.WriteToUDP([]byte("Conexion Establecida"+":"+random_port), addr)

	middleware.Close()
}

func GenerateListenConnectionToPlay() {
	for {

		address := "127.0.0.1:" + random_port
		udpAddr, _ := net.ResolveUDPAddr("udp", address)

		middleware, err := net.ListenUDP("udp", udpAddr)
		print("\naddress: ", address)
		print("\nupdAddr: ", udpAddr.IP.String(), "	Port: ", strconv.Itoa(udpAddr.Port))
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		buffer := make([]byte, 1024)
		n, addr, err := middleware.ReadFromUDP(buffer)
		print("\nMensaje: ")
		data := buffer[:n]
		if err != nil {
			fmt.Println(err)
			return
		}
		if string(data) == "Insertar" {
			column := GenerateMove()
			columnStr := strconv.Itoa(column)
			random_port = strconv.Itoa(GeneratePort())
			message := columnStr + ":" + random_port
			middleware.WriteToUDP([]byte(message), addr)
		} else if string(data) == "Desconectar" {
			middleware.WriteToUDP([]byte("Robot Desconectado:0 "), addr)
			middleware.Close()
			print("\nRobot Desconectado")
			break
		} else {
			print("\nError en el mensaje")
			break
		}

		middleware.Close()

	}
}
