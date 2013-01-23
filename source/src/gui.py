# coding: utf-8
# @author: Charles Tim Batista Garrocho
# @contact: charles.garrocho@gmail.com
# @copyright: (C) 2012-2013 Python Software Open Source

import re
import sys
import time
import settings
import botwipy
from threading import Thread
from PyQt4 import QtGui, QtCore, QtWebKit, Qt

# Conectando a API utilizando os dados da aplicação.
bot = botwipy.BotAPI()


class IniciarBot(QtCore.QThread):
    mensagem_lista = QtCore.pyqtSignal(str)
    mensagem_status_bar = QtCore.pyqtSignal(str)

    def run(self):
        while bot.RODAR:
            self.mensagem_status_bar.emit('Obtendo Lista de Mensagens dos Meus Seguidores')
            amigos_tweets = bot.get_amigos_tweets()
            for tweet in amigos_tweets:
                self.mensagem_status_bar.emit(tweet.text)
                usuario = bot.verifica_tweet(tweet, 'RT @(.*?):')
                if usuario is not None:
                    self.mensagem_lista.emit('<b style="float:left">{0}</b><i style="float:right"> <font color="#20B2AA">{1}</font> </i> <br>{2}'.format(bot.get_meu_nome(), usuario[1], bot.seguir_usuario(usuario[0])))
            self.mensagem_status_bar.emit('Obtendo Lista de Minhas Mensoes')
            for usuario in bot.get_mensoes():
                self.mensagem_lista.emit('<b>{0}</b> <br> {1}'.format(bot.get_meu_nome(), bot.seguir_usuario(usuario[1])))
                novo_status = u'Ola @{0}. Obrigado pela sua mensagem! :-)'.format(usuario[1])
                self.mensagem_lista.emit('<b>{0}</b> <br> Atualizou seu Status para: {1}'.format(bot.get_meu_nome(), novo_status))
                bot.atualizar_status(novo_status)
            time.sleep(2)


class PararBot(QtCore.QThread):
    mensagem_status_bar = QtCore.pyqtSignal(str)
    
    def run(self):
        bot.RODAR = False
        #bot.get_followers()


class JanelaInicial(QtGui.QMainWindow):
    """
    Essa é a Interface gráfica inicial do botwipy. Nela é definido uma barra de
    botões o carregamento de uma lista de um arquivo html e a barra de status.
    """

    def __init__(self):
        super(JanelaInicial, self).__init__()
        self.iniciar()
        self.adicionar()
        self.pIniciar = IniciarBot()
        self.pIniciar.mensagem_lista.connect(self.recebe_msg_init_lista)
        self.pIniciar.mensagem_status_bar.connect(self.recebe_msg_init_status)
        self.pParar = PararBot()
        self.pParar.mensagem_status_bar.connect(self.recebe_msg_init_status)
        self.configurar()
   
    def recebe_msg_init_lista(self, mensagem):
        self.webView.page().mainFrame().evaluateJavaScript('novoElemento("%s")' % (mensagem,))

    def recebe_msg_init_status(self, mensagem):
        self.statusBar().showMessage(mensagem)

    def iniciar(self):
    
        self.webView = QtWebKit.QWebView()
        
        self.html = open(settings.HTML).read()
        
        self.iniciarBot = QtGui.QAction(QtGui.QIcon(settings.INICIAR), 'Iniciar', self)
        self.iniciarBot.setShortcut('Ctrl+I')
        self.iniciarBot.setStatusTip('Iniciar o Bot - Ctrl+I')
        self.iniciarBot.triggered.connect(self.iniciar_bot)
        
        self.pararBot = QtGui.QAction(QtGui.QIcon(settings.PARAR), 'Parar', self)
        self.pararBot.setShortcut('Ctrl+P')
        self.pararBot.setStatusTip('Parar o Bot - Ctrl+P')
        self.pararBot.triggered.connect(self.parar_bot)
        
        self.confBot = QtGui.QAction(QtGui.QIcon(settings.CONFIGURAR), 'Configurar', self)
        self.confBot.setShortcut('Ctrl+C')
        self.confBot.setStatusTip('Configurar o Bot - Ctrl+C')
        #self.confBot.triggered.connect(self.close)
        
        self.atuaBot = QtGui.QAction(QtGui.QIcon(settings.LIMPAR), 'Limpar', self)
        self.atuaBot.setShortcut('Ctrl+A')
        self.atuaBot.setStatusTip('Atualizar Twitter - Ctrl+A')
        self.atuaBot.triggered.connect(self.limpar_lista)
        
        self.keysBot = QtGui.QAction(QtGui.QIcon(settings.CHAVES), 'Chaves', self)
        self.keysBot.setShortcut('Ctrl+K')
        self.keysBot.setStatusTip('Chaves do Bot - Ctrl+K')
        self.keysBot.triggered.connect(self.chamar_chaves)
        
        self.sobre = QtGui.QAction(QtGui.QIcon(settings.AJUDA), 'Sobre', self)
        self.sobre.setShortcut('Ctrl+H')
        self.sobre.setStatusTip('Sobre o BotWiPy - Ctrl+S')
        self.sobre.triggered.connect(self.chamar_sobre)
        
        self.sair = QtGui.QAction(QtGui.QIcon(settings.SAIR), 'Sair', self)
        self.sair.setShortcut('Ctrl+Q')
        self.sair.setStatusTip('Sair da Aplicacao - Ctrl+Q')
        self.sair.triggered.connect(self.close)

        self.toolBar = self.addToolBar('Sair')
        self.statusBar()

    def adicionar(self):
        
        self.webView.setHtml(self.html)
        self.setCentralWidget(self.webView)
        
        self.toolBar.addAction(self.iniciarBot)
        self.toolBar.addAction(self.pararBot)
        self.toolBar.addAction(self.atuaBot)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.keysBot)
        self.toolBar.addAction(self.confBot)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.sobre)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.sair)

    def configurar(self):
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setFixedSize(620, 700)
        self.setWindowTitle('BOTWIPY - Bot em Python Para Twitter')
        self.setWindowIcon(QtGui.QIcon(settings.LOGO))
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        self.show()
    
    def iniciar_bot(self):
        bot.RODAR = True
        self.pIniciar.start()

    def parar_bot(self):
        self.pParar.start()
    
    def limpar_lista(self):
        self.webView.page().mainFrame().evaluateJavaScript('LimparLista()')
    
    def chamar_sobre(self):
        exSobre = DialogoSobre()
        exSobre.exec_()

    def chamar_chaves(self):
        exChaves = DialogoChaves()
        exChaves.exec_()

    def chamar_followers(self):
        exFollowers = DialogoFollowers()
        exFollowers.exec_()

class DialogoSobre(QtGui.QDialog):
    """
    Essa é a Interface gráfica do dialogo sobre, onde contém as informações de
    software. Nela é definido vários rótulos e uma imagem logo do software.
    """
    
    def __init__(self):
        super(DialogoSobre, self).__init__()
        self.iniciar()
        self.adicionar()
        self.configurar()
        
    def iniciar(self):
        self.vbox = QtGui.QHBoxLayout()                                        
        self.setLayout(self.vbox)
          
        self.foto_label = QtGui.QLabel()
        self.foto_label.setPixmap(QtGui.QPixmap(settings.LOGO))
        self.label = QtGui.QLabel('<H3>Informacoes do software</H3> <b>Software: </b>Bot Twitter em Python <br> <b>Versao: </b> 1.0 <br> <b>Copyright: </b>Open Source<br> <H3>Desenvolvedores</H3> Charles Tim Batista Garrocho <br>Paulo Vitor Francisco')
        
    def adicionar(self):
        self.vbox.addWidget(self.foto_label)
        self.vbox.addWidget(self.label)

    def configurar(self):
        self.setModal(True)
        self.setWindowTitle('BoTiWiPy - Sobre o Software')
        self.setWindowIcon(QtGui.QIcon(settings.LOGO))
        self.setFixedSize(410, 215)
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        self.size = self.geometry()
        self.move((self.screen.width() - self.size.width()) / 2, (self.screen.height() - self.size.height()) / 2)
        self.show()


class DialogoChaves(QtGui.QDialog):
    """
    Essa é a Interface gráfica do dialogo de definição de chaves para o acesso
    a conta twitter. Nela é definido vários rótulos e campos de texto e botões.
    """
    
    def __init__(self):
        super(DialogoChaves, self).__init__()
        self.iniciar()
        self.adicionar()
        self.configurar()
        
    def iniciar(self):
        self.boxTotal = QtGui.QVBoxLayout()
        self.boxRotuloCampo = QtGui.QHBoxLayout()
        self.boxRotulo = QtGui.QVBoxLayout()
        self.boxCampo = QtGui.QVBoxLayout()
        self.boxBotao = QtGui.QHBoxLayout()
        
        self.botaoGravar = QtGui.QPushButton(QtGui.QIcon(settings.GRAVAR), 'Gravar')
        self.botaoGravar.setIconSize(QtCore.QSize(30,30));
        
        self.botaoCancelar = QtGui.QPushButton(QtGui.QIcon(settings.CANCELAR), 'Cancelar')
        self.botaoCancelar.setIconSize(QtCore.QSize(30,30));
        
        self.botaoLimpar = QtGui.QPushButton(QtGui.QIcon(settings.LIMPAR), 'Limpar')
        self.botaoLimpar.setIconSize(QtCore.QSize(30,30));
        
        self.rotuloConsumerKey = QtGui.QLabel('Consumer Key')
        self.campoTextoConsumerKey = QtGui.QLineEdit(settings.CONSUMER_KEY)
        
        self.rotuloConsumerSecret = QtGui.QLabel('Consumer Secret')
        self.campoTextoConsumerSecret = QtGui.QLineEdit(settings.CONSUMER_SECRET)

        self.rotuloAcessToken = QtGui.QLabel('Acess Token')
        self.campoTextoAcessToken = QtGui.QLineEdit(settings.OAUTH_TOKEN)
        
        self.rotuloAcessTokenSecret = QtGui.QLabel('Acess Token Secret')
        self.campoTextoAcessTokenSecret = QtGui.QLineEdit(settings.OAUTH_TOKEN_SECRET)

    def adicionar(self):
        self.boxTotal.addWidget(QtGui.QLabel('<b>Defina</b> abaixo as chaves de seguranca da <b>conta Twitter</b>'))
        self.boxRotulo.addWidget(self.rotuloConsumerKey)
        self.boxCampo.addWidget(self.campoTextoConsumerKey)
        
        self.boxRotulo.addWidget(self.rotuloConsumerSecret)
        self.boxCampo.addWidget(self.campoTextoConsumerSecret)
        
        self.boxRotulo.addWidget(self.rotuloAcessToken)
        self.boxCampo.addWidget(self.campoTextoAcessToken)
        
        self.boxRotulo.addWidget(self.rotuloAcessTokenSecret)
        self.boxCampo.addWidget(self.campoTextoAcessTokenSecret)
        
        self.boxBotao.addWidget(self.botaoGravar)
        self.boxBotao.addWidget(self.botaoLimpar)
        self.boxBotao.addWidget(self.botaoCancelar)

        self.boxRotuloCampo.addLayout(self.boxRotulo)
        self.boxRotuloCampo.addLayout(self.boxCampo)
        
        self.boxTotal.addLayout(self.boxRotuloCampo)

        self.boxTotal.addLayout(self.boxBotao)
        
        self.setLayout(self.boxTotal)

    def configurar(self):
        self.setModal(True)
        self.setWindowTitle('BoTiWiPy - Chaves de Seguranca')
        self.setWindowIcon(QtGui.QIcon(settings.LOGO))
        self.setFixedSize(400, 240)
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        self.size = self.geometry()
        self.move((self.screen.width() - self.size.width()) / 2, (self.screen.height() - self.size.height()) / 2)
        self.show()

    def gravar(self):
        # re.sub("JegRGulzhvp09grgBtPNaMeuvyPvYKwTkPRrz0X1c", "KKKKKKKKKKKKKKKKKKKKKKKKKKK", a)
        self.campoTextoConsumerSecret.text()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = JanelaInicial()
    sys.exit(app.exec_())
